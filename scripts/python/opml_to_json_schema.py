import argparse
from collections import OrderedDict

import json
import xml.etree.ElementTree as ElementTree


ATTRIBS_TO_IMPORT = ['description', 'unique', 'autogenerated', 'enum' 'const', 'type', 'format', 'ontology', 'namespace', 'foreignProperty', 'matchType']
ALWAYS_ARRAY_ATTIBS = ['examples']
ARRAY_SPLIT_TEXT = '|'
MAX_EXAMPLES_COUNT = 4
BOOLEAN_MAP = {'true': True, 'false': False}


def json_schema_create_root():
    json_dict = OrderedDict()
    json_dict['$schema'] = "http://json-schema.org/draft-07/schema#"
    json_dict['$id'] = "https://raw.githubusercontent.com/fairtracks/fairtracks_standard/master/json/schema/fairtracks.schema.json"
    json_dict['title'] = "FAIRification of Genomic Tracks JSON Schema"
    json_dict['type'] = 'object'
    return json_dict


def json_schema_add_end_root_attribs(json_dict):
    json_dict['additionalProperties'] = True
    json_dict['primary_key'] = []
    json_dict['dependencies'] = {}
    return json_dict


def json_schema_handle_visit(element, json_parent, array_index=None):
    json_child = OrderedDict()
    print(str(element))

    def add_attrib(json_child, attrib_name):
        if attrib_name in element.attrib:
            element_value = element.attrib[attrib_name]
            if element_value:
                if element_value in BOOLEAN_MAP.keys():
                    json_child[attrib_name] = BOOLEAN_MAP[element_value]
                elif ARRAY_SPLIT_TEXT in element_value or attrib_name in ALWAYS_ARRAY_ATTIBS:
                    json_child[attrib_name] = [_ for _ in element_value.split(ARRAY_SPLIT_TEXT)]
                else:
                    json_child[attrib_name] = element_value

    for attrib in ATTRIBS_TO_IMPORT:
        add_attrib(json_child, attrib)

    if element.attrib['type'] == 'array':
        json_child['items'] = OrderedDict()

    if 'items' in json_parent:
        json_parent['items'] = json_child
    else:
        if 'properties' not in json_parent:
            json_parent['properties'] = OrderedDict()

        key = element.attrib['text']
        json_parent['properties'][key] = json_child

        if element.attrib['required'] == 'true':
            if 'required' not in json_parent:
                json_parent['required'] = []
            json_parent['required'].append(key)

    return json_child


def json_example_handle_visit(element, json_parent, array_index):
    el_type = element.attrib['type']

    if el_type == 'object':
        json_child = OrderedDict()
    elif el_type == 'array':
        json_child = []
    else:
        el_examples = element.attrib.get('examples')
        el_default = element.attrib.get('default')
        el_const = element.attrib.get('const')

        if el_examples:
            content = el_examples
        elif el_default:
            content = el_default
        elif el_const:
            content = el_const
        else:
            return
            raise ValueError('Missing example content for element: ' + element.attrib['text'])

        if array_index is not None:
            split_content = content.split(ARRAY_SPLIT_TEXT)
            if array_index < len(split_content):
                json_child = split_content[array_index]
            else:
                return
        else:
            json_child = content

    if isinstance(json_parent, dict):
        if element.attrib['text'] not in json_parent:
            json_parent[element.attrib['text']] = json_child
        else:
            json_child = json_parent[element.attrib['text']]
    else:
        print(json_parent)
        json_parent.append(json_child)

    return json_child


def visit_opml_outline_elements(opml_root, visit_func, json_parent, array_index=None):
    for opml_elem in opml_root.getchildren():
        json_child = visit_func(opml_elem, json_parent, array_index)
        visit_opml_outline_elements(opml_elem, visit_func, json_child, array_index)


parser = argparse.ArgumentParser(description='Generate JSON schema and example '
                                             'JSON from OPML definition file')
parser.add_argument('in_definition', type=argparse.FileType('r'))
parser.add_argument('out_schema', type=argparse.FileType('w'))
parser.add_argument('out_example', type=argparse.FileType('w'))
args = parser.parse_args()

opml_root = ElementTree.parse(args.in_definition.name).find('./body')

json_schema_dict = json_schema_create_root()
visit_opml_outline_elements(opml_root, json_schema_handle_visit, json_schema_dict)
json_schema_dict = json_schema_add_end_root_attribs(json_schema_dict)
args.out_schema.write(json.dumps(json_schema_dict, indent=4))

json_example_dict = OrderedDict()
for array_index in range(MAX_EXAMPLES_COUNT):
    visit_opml_outline_elements(opml_root, json_example_handle_visit, json_example_dict, array_index)
# json_example_dict = json_example_add_end_root_attribs(json_example_dict)
args.out_example.write(json.dumps(json_example_dict, indent=4))
