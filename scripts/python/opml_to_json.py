import argparse
import io
import hashlib
import json
import os
import xml.etree.ElementTree as ElementTree

from collections import OrderedDict
from datetime import datetime

from json_signature import compute_signature_from_json_content

ATTRIBS_TO_IMPORT = [
    'description',
    'type',
    'format',
    'pattern',
    'enum',
    'const',
    'default',
    'ontology',
    'namespace',
    'matchType',
    'examples',
    'foreignProperty',
    'ref',
    'autogenerated',
    'unique',
    'minItems'
]
ATTRIB_CONVERT_MAPPINGS = {'ref': '$ref'}
INTEGER_ATTRIBS = ['minItems']
ALWAYS_ARRAY_ATTRIBS = ['examples']
NEVER_ARRAY_ATTRIBS = ['pattern']
ARRAY_SPLIT_CHAR_LEVEL_1 = '|'
ARRAY_SPLIT_CHAR_LEVEL_2 = ';'
MAX_EXAMPLES_COUNT = 4
BOOLEAN_MAP = {'true': True, 'false': False}


# Public methods

def main():
    parser = argparse.ArgumentParser(description='Generate JSON schema or example '
                                                 'JSON from OPML overview file')
    parser.add_argument('json_type', choices=['schema', 'single_example', 'full_example'])
    parser.add_argument('in_opml', type=argparse.FileType('r'))
    parser.add_argument('out_json', type=argparse.FileType('r+'))
    args = parser.parse_args()

    if args.json_type == 'schema':
        json_dict = create_json_schema_dict(args.in_opml.name)
    elif args.json_type == 'single_example':
        json_dict = create_json_example_dict(args.in_opml.name, example_index=0)
    else:  # full_example
        json_dict = create_json_example_dict(args.in_opml.name)

    if_changed_write_json_file(args.out_json, json_dict)


def create_json_schema_dict(opml_path):
    opml_root = ElementTree.parse(opml_path).find('./body')

    json_schema_dict = _json_schema_create_root(opml_root)
    _json_schema_create_subtree(opml_root, json_parent=json_schema_dict)
    json_schema_dict = _json_schema_add_end_root_attribs(json_schema_dict)
    json_schema_dict = _json_schema_add_signature(json_schema_dict)

    return json_schema_dict


def create_json_example_dict(opml_path, example_index=None):
    opml_root = ElementTree.parse(opml_path).find('./body')

    json_example_dict = OrderedDict()
    _json_example_create_subtree(opml_path, opml_root,
                                 json_parent=json_example_dict,
                                 example_index=example_index)

    json_example_dict = _json_example_add_doc_info_attribs(json_example_dict)
    json_example_dict = _json_example_add_signature(json_example_dict)

    return json_example_dict


def if_changed_write_json_file(json_file, json_dict):
    new_signature = compute_signature_from_json_content(json_dict)
    try:
        old_signature = compute_signature_from_json_content(json.load(json_file))
        do_write = new_signature != old_signature
    except json.decoder.JSONDecodeError:
        from traceback import print_exc
        print_exc()
        do_write = True

    if do_write:
        json_file.seek(0)
        json_file.truncate()
        json_file.write(json.dumps(json_dict, indent=4))
    else:
        os.utime(json_file.name)


# JSON schema internal methods

def _json_schema_create_root(opml_root):
    json_dict = OrderedDict()
    json_dict['$schema'] = "http://json-schema.org/draft-07/schema#"
    json_dict['$id'] = opml_root.find(".//outline[@_text='@schema']").attrib['const']
    json_dict['$comment'] = ""
    json_dict['title'] = opml_root.find(".//outline[@_text='#title']").attrib['const']
    json_dict['type'] = 'object'
    return json_dict


def _json_schema_create_subtree(opml_root, json_parent):
    for opml_elem in opml_root:
        json_child = _json_schema_create_child(opml_elem)
        _json_schema_create_subtree(opml_root=opml_elem, json_parent=json_child)
        _json_schema_add_child_to_parent(opml_elem, json_child, json_parent)


def _json_schema_create_child(opml_elem):
    json_child = OrderedDict()

    for attrib in ATTRIBS_TO_IMPORT:
        _json_schema_add_attrib_to_child(opml_elem, json_child, attrib)

    if 'type' in opml_elem.attrib and opml_elem.attrib['type'] == 'array':
        json_child['items'] = OrderedDict()

    return json_child


def _json_schema_add_attrib_to_child(opml_elem, json_child, attrib_name):
    if attrib_name in opml_elem.attrib:
        element_value = opml_elem.attrib[attrib_name]
        if attrib_name in ATTRIB_CONVERT_MAPPINGS:
            attrib_name = ATTRIB_CONVERT_MAPPINGS[attrib_name]
        if element_value:
            if element_value in BOOLEAN_MAP.keys():
                json_child[attrib_name] = BOOLEAN_MAP[element_value]
            elif attrib_name in ALWAYS_ARRAY_ATTRIBS or \
                    (ARRAY_SPLIT_CHAR_LEVEL_1 in element_value and
                     attrib_name not in NEVER_ARRAY_ATTRIBS):
                json_child[attrib_name] = element_value.split(ARRAY_SPLIT_CHAR_LEVEL_1)
            elif attrib_name in INTEGER_ATTRIBS:
                json_child[attrib_name] = int(element_value)
            else:
                json_child[attrib_name] = element_value


def _json_schema_add_child_to_parent(element, json_child, json_parent):
    if 'items' in json_parent:
        json_parent['items'] = json_child
    else:
        if 'properties' not in json_parent:
            json_parent['properties'] = OrderedDict()

        if _ignore_element(element):
            return

        key = element.attrib['_text']
        json_parent['properties'][key] = json_child

        if element.attrib['required'] == 'true':
            if 'required' not in json_parent:
                json_parent['required'] = []
            json_parent['required'].append(key)

        if 'anyOf' in element.attrib and element.attrib['anyOf'] == 'true':
            if 'anyOf' not in json_parent:
                json_parent['anyOf'] = []
            json_parent['anyOf'].append({'required': [key]})


def _json_schema_add_end_root_attribs(json_dict):
    json_dict['additionalProperties'] = True
    # json_dict['primary_key'] = []
    return json_dict


def _json_schema_add_signature(json_dict):
    signature = compute_signature_from_json_content(json_dict)
    json_dict['$comment'] = "JSON signature: " + signature
    return json_dict


# JSON example internal methods

def _json_example_create_subtree(opml_path, opml_root, json_parent, example_index):
    num_children_created = 0

    for opml_elem in opml_root:
        if _ignore_element(opml_elem):
            continue

        json_child = None
        if _is_ref(opml_elem):
            json_child = _json_example_get_child_for_ref(
                opml_path, opml_elem, example_index)
        else:
            json_elem_array = _json_example_convert_opml_elem_to_json_array(opml_elem)
            if json_elem_array:
                json_child = _json_example_get_child_recursively(
                    opml_path, opml_elem, json_elem_array, example_index)
        if json_child:
            _json_example_add_child_to_parent(opml_elem, json_child, json_parent)
            num_children_created += 1

    return num_children_created


def _json_example_get_child_for_ref(opml_path, opml_elem, example_index):
    ref_opml_path = _generate_opml_path_from_ref(opml_path, opml_elem)
    json_child = create_json_example_dict(ref_opml_path, example_index=example_index)
    if "@schema" in json_child:
        del json_child['@schema']
    return json_child


def _json_example_add_child_to_parent(element, json_child, json_parent):
    if isinstance(json_parent, dict):
        key = element.attrib['_text']
        json_parent[key] = json_child
    else:  # array
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


def _json_example_get_child_recursively(opml_path, opml_elem, json_elem_array, example_index):
    json_child = json_elem_array[example_index if example_index is not None else 0]
    if _is_example_content(json_elem_array):
        return json_child

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
                opml_path,
                opml_root=opml_elem,
                json_parent=json_child,
                example_index=grandchild_example_index
            )
        except IndexError:
            pass

    # Pruning empty branches
    if num_grandchildren_created > 0:
        return json_child


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

def _ignore_element(opml_elem):
    key = opml_elem.attrib.get('_text')
    if key:
        return key.startswith('#')
    else:
        return False


def _is_ref(opml_elem):
    return 'ref' in opml_elem.attrib


def _generate_opml_path_from_ref(opml_path, opml_elem):
    return os.path.join(
        os.path.dirname(opml_path),
        os.path.basename(_get_ref(opml_elem)).replace('.schema.json', '.overview.opml')
    )


def _get_ref(opml_elem):
    return opml_elem.attrib['ref']


def _is_array(json_child):
    return isinstance(json_child, list)


if __name__ == "__main__":
    main()
