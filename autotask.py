import requests
import xmltodict
from requests.auth import HTTPBasicAuth
from toolz import get_in


class Autotask():
    username = ''
    password = ''

    @staticmethod
    def get_xml_field_value(field_name, data, mode='query'):
        entity_path = [
            'soap:Envelope',
            'soap:Body',
            f'{mode}Response',
            f'{mode}Result',
            'EntityResults',
            'Entity'
        ]
        if field_name == 'id':
            return get_in(entity_path + [field_name], data)

        return get_in(entity_path + [field_name, '#text'], data)

    def _request(self, data):
        url = 'https://webservices2.autotask.net/atservices/1.5/atws.asmx'
        headers = {'Content-Type': 'text/xml'}
        auth = HTTPBasicAuth(self.username, self.password)

        res = requests.post(url, data, headers=headers, auth=auth)

        return xmltodict.parse(res.text)

    def extract_response_from_keys(self, response_body, select_fields, mode):
        entity = {}
        for key in select_fields:
            entity[key] = self.get_xml_field_value(key, response_body, mode)
        return entity

    def query(self, entity, filter_field, filter_value, select_fields=()):
        with open('templates/query.xml', 'r') as xml_file:
            xml_template = xml_file.read()

        data = xml_template.format(
            entity=entity,
            filter_field=filter_field,
            filter_value=filter_value
        )

        response_body = self._request(data)

        entity = self.extract_response_from_keys(
            response_body, select_fields, mode='query'
        )
        return entity

    def create(self, entity, update_object, select_fields=()):
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

        response_body = self._request(data)

        entity = self.extract_response_from_keys(
            response_body, select_fields, mode='create'
        )
        return entity

    def update(self, entity, lookup_keys, field, value, select_fields=()):
        create_procedure = {
            'soap:Envelope': {
                '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                '@xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
                '@xmlns:soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'soap:Body': {
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
            }
        }
        data = xmltodict.unparse(create_procedure)

        response_body = self._request(data)

        entity = self.extract_response_from_keys(
            response_body, select_fields, mode='update'
        )
        return entity
