import argparse
import io
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ElementTree

from collections import OrderedDict, namedtuple, defaultdict
from copy import copy
from datetime import datetime

from json_signature import compute_signature_from_json_content

ATTRIBS_TO_IMPORT = [
    'title',
    'description',
    'type',
    'format',
    'pattern',
    'enum',
    'const',
    'default',
    'ontology',
    'ancestors',
    'namespace',
    'matchType',
    'examples',
    'foreignProperty',
    'ref',
    'unique',
    'autogenerated',
    'minItems'
]
ATTRIB_CONVERT_MAPPINGS = {'ref': '$ref'}
INTEGER_ATTRIBS = ['minItems']
ALWAYS_ARRAY_ATTRIBS = ['examples']
NEVER_ARRAY_ATTRIBS = ['pattern']
IF_THEN_ATTRIBS = ['constIf', 'requireIf']
ARRAY_SPLIT_CHAR_LEVEL_1 = '|'
ARRAY_SPLIT_CHAR_LEVEL_2 = ';'
MAX_EXAMPLES_COUNT = 4
EXAMPLE_SKIP_CHAR = '.'
BOOLEAN_MAP = {'true': True, 'false': False}


# Helper classes

class NestedOrderedDict(OrderedDict):
    """
    OrderedDict that automatically enlarges itself when needed.
    Copied from https://stackoverflow.com/a/18809656
    """
    def __missing__(self, key):
        val = self[key] = NestedOrderedDict()
        return val


RuleCategory = namedtuple('RuleCategory', ('if_pointer', 'then_pointer', 'then_value'))


class ArgumentParserError(Exception): pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)


# Public methods

def main():
    try:
        args = _parseArgs(out_file_mode='r+')
    except ArgumentParserError:
        try:
            args = _parseArgs(out_file_mode='w')
        except ArgumentParserError as e:
            print('Error - {}'.format(e), file=sys.stderr)
            sys.exit(1)

    if args.json_type == 'schema':
        json_dict = create_json_schema_dict(args.in_opml.name)
    elif args.json_type == 'single_example':
        json_dict = create_json_example_dict(args.in_opml.name, example_index=0)
    else:  # full_example
        json_dict = create_json_example_dict(args.in_opml.name)

    if_changed_write_json_file(args.out_json, json_dict)


def _parseArgs(out_file_mode):
    parser = ThrowingArgumentParser(description='Generate JSON schema or example '
                                                'JSON from OPML overview file')
    parser.add_argument('json_type', choices=['schema', 'single_example', 'full_example'])
    parser.add_argument('in_opml', type=argparse.FileType('r'))
    parser.add_argument('out_json', type=argparse.FileType(out_file_mode))
    return parser.parse_args()


def create_json_schema_dict(opml_file_path):
    opml_root = ElementTree.parse(opml_file_path).find('./body')

    json_schema_dict = _json_schema_create_root(opml_root)
    _json_schema_create_subtree(opml_root, json_parent=json_schema_dict, json_path=[])
    json_schema_dict = _json_schema_add_end_root_attribs(json_schema_dict)
    json_schema_dict = _json_schema_add_signature(json_schema_dict)

    return json_schema_dict


def create_json_example_dict(opml_file_path, example_index=None):
    opml_root = ElementTree.parse(opml_file_path).find('./body')

    json_example_dict = NestedOrderedDict()
    _json_example_create_subtree(opml_file_path, opml_root,
                                 json_parent=json_example_dict,
                                 example_index=example_index)

    json_example_dict = _json_example_add_doc_info_attribs(json_example_dict)
    json_example_dict = _json_example_add_signature(json_example_dict)

    return json_example_dict


def if_changed_write_json_file(json_file, json_dict):
    new_signature = compute_signature_from_json_content(json_dict)
    try:
        try:
            old_json_dict = json.load(json_file)
        except (io.UnsupportedOperation, json.JSONDecodeError):
            old_json_dict = {}
        old_signature_from_content = compute_signature_from_json_content(old_json_dict)
        old_signature_stored = _json_dict_extract_signature(old_json_dict)
        do_write = (new_signature != old_signature_from_content) or \
            (new_signature != old_signature_stored)
    except json.decoder.JSONDecodeError:
        from traceback import print_exc
        print_exc()
        do_write = True

    if do_write:
        json_file.seek(0)
        json_file.truncate()
        json_file.write(json.dumps(json_dict, indent=4) + '\n')
        json_file.flush()
    else:
        os.utime(json_file.name)


# JSON schema internal methods

def _json_schema_create_root(opml_root):
    json_dict = NestedOrderedDict()
    json_dict['$schema'] = "http://json-schema.org/draft-07/schema#"
    json_dict['$id'] = opml_root.find(".//outline[@_name='@schema']").attrib['const']
    json_dict['$comment'] = ""
    json_dict['title'] = opml_root.find(".//outline[@_name='#toplevel']").attrib['title']
    json_dict['type'] = opml_root.find(".//outline[@_name='#toplevel']").attrib['type']
    return json_dict


def _json_schema_create_subtree(opml_parent, json_parent, json_path):
    for opml_child in opml_parent:
        json_child = _json_schema_create_child(opml_child)
        parent_name = _get_opml_el_name(opml_parent)
        child_json_path = json_path + [parent_name] if parent_name else json_path
        _json_schema_create_subtree(opml_parent=opml_child,
                                    json_parent=json_child,
                                    json_path=child_json_path)
        _json_schema_add_child_to_parent(
            opml_child, opml_parent, json_child, json_parent, child_json_path
        )


def _json_schema_create_child(opml_child):
    json_child = NestedOrderedDict()

    for attrib in ATTRIBS_TO_IMPORT:
        _json_schema_add_attrib_to_child(opml_child, json_child, attrib)

    if 'type' in opml_child.attrib and opml_child.attrib['type'] == 'array':
        json_child['items'] = NestedOrderedDict()

    if 'examples' in opml_child.attrib and opml_child.attrib['examples'] == EXAMPLE_SKIP_CHAR:
        del json_child['examples']

    return json_child


def _json_schema_add_attrib_to_child(opml_child, json_child, attrib_name):
    if attrib_name in opml_child.attrib:
        attrib_value = opml_child.attrib[attrib_name]
        if attrib_name in ATTRIB_CONVERT_MAPPINGS:
            attrib_name = ATTRIB_CONVERT_MAPPINGS[attrib_name]
        if attrib_value:
            if attrib_value in BOOLEAN_MAP.keys():
                json_child[attrib_name] = BOOLEAN_MAP[attrib_value]
            elif attrib_name in ALWAYS_ARRAY_ATTRIBS or \
                    (ARRAY_SPLIT_CHAR_LEVEL_1 in attrib_value and
                     attrib_name not in NEVER_ARRAY_ATTRIBS):
                json_child[attrib_name] = attrib_value.split(ARRAY_SPLIT_CHAR_LEVEL_1)
            elif attrib_name in INTEGER_ATTRIBS:
                json_child[attrib_name] = int(attrib_value)
            else:
                json_child[attrib_name] = attrib_value


def _json_schema_add_child_to_parent(opml_child, opml_parent, json_child, json_parent, json_path):
    if _ignore_element(opml_child):
        return

    if 'items' in json_parent:
        json_parent['items'] = json_child
    else:
        child_name = _get_opml_el_name(opml_child)
        json_parent['properties'][child_name] = json_child

        _json_schema_update_parent_required(json_parent, opml_child)
        _json_schema_update_parent_require_anyof(json_parent, opml_child)
        _json_schema_update_parent_ifthen(json_parent, opml_child,
                                          json_path + [child_name], if_level=1)


def _json_schema_update_parent_required(json_parent, opml_child):
    if opml_child.attrib['required'] == 'true':
        if 'required' not in json_parent:
            json_parent['required'] = []
        json_parent['required'].append(_get_opml_el_name(opml_child))


def _json_schema_update_parent_require_anyof(json_parent, opml_child):
    if 'requireAnyOf' in opml_child.attrib and opml_child.attrib['requireAnyOf'] == 'true':
        if 'anyOf' not in json_parent:
            json_parent['anyOf'] = []
        json_parent['anyOf'].append({'required': [_get_opml_el_name(opml_child)]})


def _json_schema_update_parent_ifthen(json_parent, opml_child, json_path, if_level):
    for opml_grandchild in opml_child:
        grandchild_name = _get_opml_el_name(opml_grandchild)
        _json_schema_update_parent_ifthen(json_parent, opml_grandchild,
                                          json_path + [grandchild_name], if_level+1)

    for if_then_attrib in IF_THEN_ATTRIBS:
        if if_then_attrib in opml_child.attrib and opml_child.attrib[if_then_attrib] != '':
            el_name = _get_opml_el_name(opml_child)
            full_attrib = opml_child.attrib[if_then_attrib]
            all_rules = re.findall(r'\|?'
                                   r'(\d(?:/\w+)*)'  # if_pointer
                                   r'='
                                   r'([\w\/\:\.]+)'  # if_value
                                   r'(?:;'  # start 'then' (constIf only)
                                   r'(0(?:/\w+)*)'  # then_pointer
                                   r'='
                                   r'([\w\/\:\.]+)'  # then_value
                                   r')?',  # end 'then'
                                   full_attrib)
            if not all_rules:
                raise ValueError('{}.{}: Not able to parse attribute value "{}"'.format(
                                 el_name, if_then_attrib, full_attrib))

            all_rules_by_category = defaultdict(list)
            for rule in all_rules:
                if_value = rule[1]
                rule_cat = RuleCategory(rule[0], rule[2], rule[3])
                all_rules_by_category[rule_cat].append(if_value)

            for cat, if_values in all_rules_by_category.items():
                assert cat.if_pointer
                level = int(cat.if_pointer[0])
                assert level > 0
                if level != if_level:
                    continue

                if 'allOf' not in json_parent:
                    json_parent['allOf'] = []

                if_then_json_object = NestedOrderedDict()
                json_parent['allOf'].append(if_then_json_object)

                cur_json_object = if_then_json_object['if']
                cur_json_object = _add_property_path_from_rel_pointer(
                    cur_json_object, json_path, cat.if_pointer
                )

                if len(if_values) == 1:
                    cur_json_object['const'] = if_values[0]
                else:
                    cur_json_object['anyOf'] = []
                    for if_value in if_values:
                        cur_json_object['anyOf'].append(NestedOrderedDict(const=if_value))

                cur_json_object = if_then_json_object['then']
                if if_then_attrib == 'requireIf':
                    cur_json_object = _add_property_path_from_rel_pointer(
                        cur_json_object, json_path, '1'
                    )
                    cur_json_object['required'] = [el_name]
                elif if_then_attrib == 'constIf':
                    assert cat.then_value
                    cur_json_object = _add_property_path_from_rel_pointer(
                        cur_json_object, json_path, cat.then_pointer
                    )
                    cur_json_object['const'] = cat.then_value


def _add_property_path_from_rel_pointer(cur_json_object, json_path, rel_pointer_str):
    rel_pointer = rel_pointer_str.split('/')
    level = int(rel_pointer[0])
    pointer_path = rel_pointer[1:] if len(rel_pointer) > 1 else []

    property_names = copy(json_path)
    property_names[len(property_names)-level:] = pointer_path

    for i, name in enumerate(property_names):
        cur_json_object = cur_json_object['properties'][name]

    return cur_json_object


def _json_schema_add_end_root_attribs(json_dict):
    json_dict['additionalProperties'] = True
    # json_dict['primary_key'] = []
    return json_dict


def _json_schema_add_signature(json_dict):
    signature = compute_signature_from_json_content(json_dict)
    json_dict['$comment'] = "JSON signature: " + signature
    return json_dict


# JSON example internal methods

def _json_example_create_subtree(opml_file_path, opml_parent, json_parent, example_index):
    num_children_created = 0

    for opml_child in opml_parent:
        if _ignore_element(opml_child):
            continue

        json_children = None
        if _is_ref(opml_child):
            json_child = _json_example_get_child_for_ref(
                opml_file_path, opml_child, example_index)
            json_children = [json_child] if json_child else None
        else:
            json_child_array = _json_example_convert_opml_elem_to_json_array(opml_child)
            if json_child_array:
                json_children = _json_example_get_children_recursively(
                    opml_file_path, opml_child, json_child_array, example_index)
        if json_children:
            _json_example_add_children_to_parent(opml_child, json_children, json_parent)
            num_children_created += len(json_children)

    return num_children_created


def _json_example_get_child_for_ref(opml_file_path, opml_parent, example_index):
    ref_opml_file_path = _generate_opml_file_path_from_ref(opml_file_path, opml_parent)
    json_child = create_json_example_dict(ref_opml_file_path, example_index=example_index)
    if '@schema' in json_child:
        del json_child['@schema']
    if 'examples' in opml_parent.attrib and opml_parent.attrib['examples'] == EXAMPLE_SKIP_CHAR:
        return None
    return json_child


def _json_example_add_children_to_parent(opml_child, json_children, json_parent):
    if isinstance(json_parent, dict):
        assert(len(json_children) == 1)
        name = _get_opml_el_name(opml_child)
        json_parent[name] = json_children[0]
    else:  # array
        for json_child in json_children:
            json_parent.append(json_child)


def _json_example_convert_opml_elem_to_json_array(opml_elem):
    """
    Convert all OPML elements to arrays for uniformity. If example data is present, the array
    length is the number of examples, if not the array length is equal to MAX_EXAMPLES_COUNT.
    Arrays are handled in _json_example_get_child_recursively() and _is_example_content().
    """
    el_type = opml_elem.attrib['type']

    if el_type == 'object':
        return [OrderedDict()] * MAX_EXAMPLES_COUNT
    elif el_type == 'array':
        return [[]] * MAX_EXAMPLES_COUNT
    else:
        el_examples = opml_elem.attrib.get('examples')
        el_const = opml_elem.attrib.get('const')
        el_default = opml_elem.attrib.get('default')

        if el_examples:
            example_array = el_examples.split(ARRAY_SPLIT_CHAR_LEVEL_1)
            for i in range(len(example_array)):
                if ARRAY_SPLIT_CHAR_LEVEL_2 in example_array[i]:
                    example_array[i] = example_array[i].split(ARRAY_SPLIT_CHAR_LEVEL_2)
            return example_array
        elif el_const:
            return [el_const] * MAX_EXAMPLES_COUNT
        elif el_default:
            return [el_default] * MAX_EXAMPLES_COUNT
        else:
            return None


def _json_example_get_children_recursively(opml_parent, opml_child, json_child_array, example_index):
    json_child = json_child_array[example_index if example_index is not None else 0]
    if _is_example_content(json_child_array):
        if _is_array(json_child):  # two-level example array, reduce a level
            return json_child
        else:
            return [json_child]

    if _is_array(json_child) and example_index is None:
        # Once example_index has been set, it will not be removed. Hence, this is the highest-level
        # array met in the current branch. As that is the case, loop through all possible examples
        # in order for grandchildren to be added to the array, one grandchild for each example
        # found.
        grandchildren_example_indices = range(MAX_EXAMPLES_COUNT)
    else:
        # Not an array. In that case, create a single grandchild, keeping the current state.
        grandchildren_example_indices = [example_index]

    # Looping through all grandchildren, adding each of them to the array.
    num_grandchildren_created = 0
    for grandchild_example_index in grandchildren_example_indices:
        try:
            num_grandchildren_created = _json_example_create_subtree(
                opml_parent,
                opml_parent=opml_child,
                json_parent=json_child,
                example_index=grandchild_example_index
            )
        except IndexError:
            pass

    # Pruning empty branches
    if num_grandchildren_created > 0:
        return [json_child]


def _is_example_content(json_elem_array):
    """
    Checks whether arrays as created in _json_example_convert_opml_elem_to_json_array() represents
    example content, assuming that the first element in the array is representative (the structure
    should be held equal in all elements).
    """
    if len(json_elem_array) == 0:
        return False

    first_content = json_elem_array[0]
    if isinstance(first_content, dict):
        return False
    elif isinstance(first_content, list):
        if len(first_content) > 0 and _is_example_content(first_content):
            # The array is a list of lists, only two levels deep. The array should then represent
            # an example for an array property.
            return True
        else:
            return False
    else:
        return True


def _json_example_add_doc_info_attribs(json_dict):
    if 'doc_info' in json_dict:
        json_dict['doc_info']['doc_version'] = ""
        json_dict['doc_info']['doc_date'] = \
            datetime.now().replace(microsecond=0).isoformat()
    return json_dict


def _json_example_add_signature(json_dict):
    if 'doc_info' in json_dict:
        signature = compute_signature_from_json_content(json_dict)
        json_dict['doc_info']['doc_version'] = signature
    return json_dict


# General helper methods

def _get_opml_el_name(element):
    return element.attrib.get('_name')


def _json_dict_extract_signature(json_dict):
    try:
        if '$schema' in json_dict:  # JSON Schema
            return json_dict['$comment'].split(': ')[-1]
        elif '@schema' in json_dict:  # JSON example
            return json_dict['doc_info']['doc_version']
    except KeyError:
        pass
    return 'No signature found!'


def _ignore_element(opml_elem):
    name = _get_opml_el_name(opml_elem)
    if name:
        return name.startswith('#')
    else:
        return False


def _is_ref(opml_elem):
    return 'ref' in opml_elem.attrib


def _generate_opml_file_path_from_ref(opml_file_path, opml_elem):
    return os.path.join(
        os.path.dirname(opml_file_path),
        os.path.basename(_get_ref(opml_elem)).replace('.schema.json', '.overview.opml')
    )


def _get_ref(opml_elem):
    return opml_elem.attrib['ref']


def _is_array(json_elem):
    return isinstance(json_elem, list)


if __name__ == "__main__":
    main()
