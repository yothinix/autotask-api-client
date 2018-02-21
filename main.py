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


def query_ticket(filter_field, filter_value):
    with open('query_ticket.xml', 'r') as xml_file:
        xml_template = xml_file.read()

    url = 'https://webservices2.autotask.net/atservices/1.5/atws.asmx'
    data = xml_template.format(
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

    ticket = {}
    for key in ('id', 'AccountID', 'CreateDate', 'DueDateTime', 'TicketNumber',
                'Title', 'Description', 'AssignedResourceID'):
        ticket[key] = get_xml_field_value(key, data)

    print(ticket)
    return ticket


query_ticket(filter_field='ticketnumber', filter_value='T20180220.0001')
