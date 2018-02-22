import os

import requests
import xmltodict
from requests.auth import HTTPBasicAuth
from toolz import get_in


def get_xml_field_value(field_name, data, mode='query'):
    entity_path = ['soap:Envelope', 'soap:Body', f'{mode}Response',
                   f'{mode}Result', 'EntityResults', 'Entity']
    if field_name == 'id':
        return get_in(entity_path + [field_name], data)

    return get_in(entity_path + [field_name, '#text'], data)


def query(entity, filter_field, filter_value, select_fields):
    with open('templates/query.xml', 'r') as xml_file:
        xml_template = xml_file.read()

    url = 'https://webservices2.autotask.net/atservices/1.5/atws.asmx'
    data = xml_template.format(
        entity=entity,
        filter_field=filter_field,
        filter_value=filter_value
    )
    headers = {'Content-Type': 'text/xml'}
    auth = HTTPBasicAuth(
        os.environ.get('AUTOTASK_USERNAME'),
        os.environ.get('AUTOTASK_PASSWORD')
    )

    res = requests.post(url, data, headers=headers, auth=auth)
    response_body = xmltodict.parse(res.text)

    entity = {}
    for key in select_fields:
        entity[key] = get_xml_field_value(key, response_body, mode='query')

    return entity


def create(entity, update_object, select_fields = []):
    url = 'https://webservices2.autotask.net/atservices/1.5/atws.asmx'

    create_procedure = {
        'soap:Envelope': {
            '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            '@xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
            '@xmlns:soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'soap:Body': {
                'create': {
                    '@xmlns': 'http://autotask.net/ATWS/v1_5/',
                    'Entities': {
                        'Entity': {
                            '@xsi:type': entity,
                            **update_object
                        }
                    }
                }
            }
        }
    }
    data = xmltodict.unparse(create_procedure)

    headers = {'Content-Type': 'text/xml'}
    auth = HTTPBasicAuth(
        os.environ.get('AUTOTASK_USERNAME'),
        os.environ.get('AUTOTASK_PASSWORD')
    )

    res = requests.post(url, data, headers=headers, auth=auth)
    response_body = xmltodict.parse(res.text)

    entity = {}
    for key in select_fields:
        entity[key] = get_xml_field_value(key, response_body, mode='create')

    return entity
