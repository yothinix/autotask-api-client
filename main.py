import os

import requests
import xmltodict
from requests.auth import HTTPBasicAuth
from toolz import get_in


def get_xml_field_value(field_name, data):
    entity_path = ['soap:Envelope', 'soap:Body', 'queryResponse',
                   'queryResult', 'EntityResults', 'Entity']
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
    data = xmltodict.parse(res.text)

    entity = {}
    for key in select_fields:
        entity[key] = get_xml_field_value(key, data)

    print(entity)
    return entity


query(
    entity='Ticket',
    filter_field='ticketnumber',
    filter_value='T20180220.0001',
    select_fields=(
        'id', 'AccountID', 'CreateDate', 'DueDateTime',
        'TicketNumber', 'Title', 'Description', 'AssignedResourceID'
    )
)
