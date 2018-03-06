import os
from collections import OrderedDict
from typing import Tuple, Union, Dict

import requests
import xmltodict
from requests.auth import HTTPBasicAuth
from toolz import get_in


ENTITY_DEFAULT_FIELDS = {
    'Ticket': ('id', 'AccountID', 'CreateDate', 'CreatorResourceID', 'DueDateTime', 'LastActivityDate',
               'Priority', 'AssignedResourceID', 'AssignedResourceRoleID', 'Status', 'TicketNumber',
               'Title', 'Resolution', 'PurchaseOrderNumber', 'TicketType', 'ChangeApprovalType',
               'LastCustomerVisibleActivityDateTime', 'TicketCategory', 'ExternalID')
}


class Autotask():
    url = 'https://webservices2.autotask.net/atservices/1.5/atws.asmx'
    headers = {'Content-Type': 'text/xml'}
    username = ''
    password = ''
    integration_code = ''
    integration_headers = {
        'soap:Header': {
            'IntegrationCode': integration_code
        }
    }
    base_xml_template = {
        'soap:Envelope': {
            '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            '@xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
            '@xmlns:soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'soap:Body': {}
        }
    }

    def _request(self, data: str) -> Tuple[int, str]:
        auth = HTTPBasicAuth(self.username, self.password)
        res = requests.post(self.url, data, headers=self.headers, auth=auth)
        return res.status_code, res.text

    @staticmethod
    def get_field_value(
            field_name: str,
            data: Dict[str, Union[str, int, Dict]],
            mode: str = 'query'
    ) -> Union[str, int]:

        entity_path = ['soap:Envelope', 'soap:Body', f'{mode}Response', f'{mode}Result', 'EntityResults', 'Entity']
        if field_name == 'id':
            return get_in(entity_path + [field_name], data)

        return get_in(entity_path + [field_name, '#text'], data)

    def extract_response_from_keys(
            self,
            response_body: Dict[str, Union[str, int, Dict]],
            select_fields: Tuple[str, ...],
            mode: str
    ) -> Dict[str, Union[str, int]]:

        entity = {}
        for key in select_fields:
            entity[key] = self.get_field_value(key, response_body, mode)

        return entity

    def query(
            self,
            entity: str,
            filter_field: str,
            filter_value: str,
            operation: str = 'equals',
            select_fields: Tuple[str, ...] = ()
    ) -> Tuple[Union[Dict, str], int]:

        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.abspath(os.path.join(current_dir, 'templates/query.xml'))
        with open(file_path, 'r') as xml_file:
            xml_template = xml_file.read()

        data = xml_template.format(
            entity=entity,
            operation=operation,
            filter_field=filter_field,
            filter_value=filter_value
        )

        status_code, body = self._request(data)

        if status_code != 200:
            return body, status_code

        entity = self.extract_response_from_keys(
            response_body=xmltodict.parse(body),
            select_fields=select_fields if select_fields else ENTITY_DEFAULT_FIELDS[entity],
            mode='query'
        )

        return entity, status_code

    def create(
        self,
        entity: str,
        update_object: Dict[str, str],
        select_fields: Tuple[str, ...] = ()
    ) -> Tuple[Union[Dict, str], int]:

        procedure = {
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

        create_procedure = self.base_xml_template.copy()
        create_procedure['soap:Envelope']['soap:Body'] = procedure

        data = xmltodict.unparse(create_procedure)

        status_code, body = self._request(data)

        if status_code != 200:
            return body, status_code

        entity = self.extract_response_from_keys(
            response_body=xmltodict.parse(body),
            select_fields=select_fields if select_fields else ENTITY_DEFAULT_FIELDS,
            mode='create'
        )

        return entity, status_code

    def update_udf(
        self,
        entity: str,
        lookup_keys: Dict[str, str],
        field: str,
        value: str,
        select_fields: Tuple[str, ...] = ()
    ) -> Tuple[Union[Dict, str], int]:
        procedure = {
            'update': {
                '@xmlns': 'http://autotask.net/ATWS/v1_5/',
                'Entities': {
                    'Entity': {
                        '@xsi:type': entity,
                        **lookup_keys,
                        'UserDefinedFields': {
                            'UserDefinedField': {
                                'Name': field,
                                'Value': value
                            }
                        }
                    }
                }
            }
        }

        create_procedure = self.base_xml_template.copy()
        create_procedure['soap:Envelope']['soap:Body'] = procedure

        data = xmltodict.unparse(create_procedure)

        status_code, body = self._request(data)

        if status_code != 200:
            return body, status_code

        entity = self.extract_response_from_keys(
            response_body=xmltodict.parse(body),
            select_fields=select_fields if select_fields else ENTITY_DEFAULT_FIELDS,
            mode='update'
        )

        return entity, status_code

    def get_zone_info(self) -> Tuple[Union[OrderedDict, str], int]:
        procedure = {
            'getZoneInfo': {
                '@xmlns': 'http://autotask.net/ATWS/v1_5/',
                'UserName': self.username
            }
        }

        base_procedure = self.base_xml_template.copy()
        base_procedure['soap:Envelope']['soap:Body'] = procedure

        data = xmltodict.unparse(base_procedure)

        status_code, body = self._request(data)

        if status_code != 200:
            return body, status_code

        keys = [
            'soap:Envelope',
            'soap:Body',
            'getZoneInfoResponse',
            'getZoneInfoResult'
        ]
        response_body = xmltodict.parse(body)
        entity = get_in(keys, response_body)

        self.url = entity['URL']

        return entity, status_code
