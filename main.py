import os

import requests
import xmltodict
from requests.auth import HTTPBasicAuth
from toolz import get_in


def get_xml_field_value(field_name, data):
    entity_path = ['soap:Envelope', 'soap:Body', 'queryResponse', 'queryResult', 'EntityResults', 'Entity']
    if field_name == 'id':
        return get_in(entity_path + [field_name], data)

    return get_in(entity_path + [field_name, '#text'], data)


def main():
    with open('query_ticket.xml', 'r') as xml_file:
        xml = xml_file.read()

    auth = HTTPBasicAuth(
        os.environ.get('AUTOTASK_USERNAME'),
        os.environ.get('AUTOTASK_PASSWORD')
    )

    res = requests.post(
       'https://webservices2.autotask.net/atservices/1.5/atws.asmx',
        data=xml.format(filter_field='ticketnumber', ticket_number='T20180220.0001'),
        headers={'Content-Type': 'text/xml'},
        auth=auth
    )

    data =xmltodict.parse(res.text)

    ticket = {}
    for key in ('AccountID', 'CreateDate', 'DueDateTime', 'TicketNumber', 'Title', 'Description', 'AssignedResourceID'):
        ticket[key] = get_xml_field_value(key, data)

    import ipdb
    ipdb.set_trace()

    print('hello world')


main()
