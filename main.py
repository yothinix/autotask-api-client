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


def hello():
    xml = """
<env:Envelope
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:tns="http://autotask.net/ATWS/v1_5/"
    xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
    <env:Body>
        <tns:query xmlns="http://autotask.net/ATWS/v1_5/">
            <sXML>
                <![CDATA[<queryxml>
                    <entity>Ticket</entity>
                    <query>
                        <field>{filter_field}
                            <expression op="equals">{ticket_number}</expression>
                        </field>
                    </query>
                </queryxml>]]>
            </sXML>
        </tns:query>
    </env:Body>
</env:Envelope>
"""

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


hello()
