from collections import OrderedDict
from unittest.mock import patch
from unittest import TestCase

from requests.auth import HTTPBasicAuth
from toolz import get_in

from utils import TestHelper
from autotask import Autotask


class AutotaskClientTest(TestCase, TestHelper):
    def setUp(self):
        self.username = 'banana@apple.com'
        self.password = 'BananaIsNotApple'
        self.autotask_client = Autotask()
        self.autotask_client.username = self.username
        self.autotask_client.password = self.password
        self.empty_response_body = '<?xml version="1.0" encoding="utf-8"?>'
        self.query_response_for_ticket_entity = {
            'soap:Envelope': {
                'soap:Body': {
                    'queryResponse': {
                        'queryResult': {
                            'EntityResults': {
                                'Entity': {
                                    'id': 1234,
                                    'AssignedResourceID': {
                                        '#text': 29682885
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        self.query_response_for_ticket_entity_as_xml = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<soap:Envelope '
            'xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
            '<soap:Body>'
            '<queryResponse xmlns="http://autotask.net/ATWS/v1_5/">'
            '<queryResult>'
            '<EntityResults>'
            '<Entity xsi:type="Ticket">'
            '<id>7872</id>'
            '<AccountID xsi:type="xsd:int">0</AccountID>'
            '<CreateDate xsi:type="xsd:dateTime">2018-02-20T01:42:57.017</CreateDate>'
            '<CreatorResourceID xsi:type="xsd:int">29683993</CreatorResourceID>'
            '<DueDateTime xsi:type="xsd:dateTime">2018-02-21T01:38:00</DueDateTime>'
            '<LastActivityDate xsi:type="xsd:dateTime">2018-02-28T04:16:06.297</LastActivityDate>'
            '<Priority xsi:type="xsd:int">1</Priority>'
            '<AssignedResourceID xsi:type="xsd:int">29682885</AssignedResourceID>'
            '<AssignedResourceRoleID xsi:type="xsd:int">29683436</AssignedResourceRoleID>'
            '<Status xsi:type="xsd:int">1</Status>'
            '<TicketNumber xsi:type="xsd:string">T20180220.0001</TicketNumber>'
            '<Title xsi:type="xsd:string">This is Man test ticket</Title>'
            '<Resolution xsi:type="xsd:string" />'
            '<PurchaseOrderNumber xsi:type="xsd:string" />'
            '<TicketType xsi:type="xsd:int">1</TicketType>'
            '<ChangeApprovalType xsi:type="xsd:int">1</ChangeApprovalType>'
            '<LastCustomerVisibleActivityDateTime xsi:type="xsd:dateTime">'
            '2018-02-28T04:16:04.797'
            '</LastCustomerVisibleActivityDateTime>'
            '<TicketCategory xsi:type="xsd:int">3</TicketCategory>'
            '<ExternalID xsi:type="xsd:string" />'
            '</Entity>'
            '</EntityResults>'
            '</queryResult>'
            '</queryResponse>'
            '</soap:Body>'
            '</soap:Envelope>'
        )

    def test_autotask_client_has_url_headers_base_xml_template_attribute_predefined(self):
        expected_url = 'https://webservices2.autotask.net/atservices/1.5/atws.asmx'
        expected_headers = {'Content-Type': 'text/xml'}
        expected_base_xml_template = {
            'soap:Envelope': {
                '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                '@xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
                '@xmlns:soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'soap:Body': {}
            }
        }

        actual = Autotask()

        self.assertEqual(actual.url, expected_url)
        self.assertDictEqual(actual.headers, expected_headers)
        self.assertDictEqual(actual.base_xml_template, expected_base_xml_template)

    def test_request_method_should_make_post_request_and_return_response_status_code_and_text(self):
        mock_response = self.mock_response(body=self.empty_response_body)
        body = '<?xml version="1.0" encoding="utf-8"?>\n' \
               '<soap:Envelope ' \
               'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
               'xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' \
               'xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">' \
               '<soap:Body>' \
               '<getZoneInfo xmlns="http://autotask.net/ATWS/v1_5/">' \
               '<UserName>banana@apple.com</UserName>' \
               '</getZoneInfo>' \
               '</soap:Body>' \
               '</soap:Envelope>'
        expected = (200, self.empty_response_body)

        with patch('requests.post', return_value=mock_response) as mock_requests:
            actual = self.autotask_client._request(body)

        self.assertTupleEqual(actual, expected)
        mock_requests.assert_called_once_with(
            'https://webservices2.autotask.net/atservices/1.5/atws.asmx',
            body,
            headers={'Content-Type': 'text/xml'},
            auth=HTTPBasicAuth(self.username, self.password)
        )

    def test_get_field_value_should_extract_value_from_soap_response_by_key(self):
        field_name = 'AssignedResourceID'
        mode = 'query'
        expected = 29682885

        with patch('autotask.get_in', side_effect=get_in) as stub_get_in:
            actual = self.autotask_client.get_field_value(field_name, self.query_response_for_ticket_entity, mode)

        self.assertEqual(actual, expected)
        stub_get_in.assert_called_once_with(
            ['soap:Envelope', 'soap:Body', 'queryResponse', 'queryResult',
             'EntityResults', 'Entity', 'AssignedResourceID', '#text'],
            self.query_response_for_ticket_entity
        )

    def test_get_field_value_for_id_key_should_not_include_text_in_entity_path(self):
        field_name = 'id'
        mode = 'query'
        expected = 1234

        with patch('autotask.get_in', side_effect=get_in) as stub_get_in:
            actual = self.autotask_client.get_field_value(field_name, self.query_response_for_ticket_entity, mode)

        self.assertEqual(actual, expected)
        stub_get_in.assert_called_once_with(
            ['soap:Envelope', 'soap:Body', 'queryResponse',
             'queryResult', 'EntityResults', 'Entity', 'id'],
            self.query_response_for_ticket_entity
        )

    def test_extract_response_from_keys_should_return_new_dict_from_response_body_filtered_by_select_fields(self):
        expected = {'id': 1234, 'AssignedResourceID': 29682885}

        actual = self.autotask_client.extract_response_from_keys(
            self.query_response_for_ticket_entity,
            select_fields=('id', 'AssignedResourceID'),
            mode='query'
        )

        self.assertEqual(actual, expected)

    def test_query_without_select_fields_should_return_all_field_belong_to_entity_and_status_code(self):
        response_from_autotask = (
            200,
            self.query_response_for_ticket_entity_as_xml
        )
        expected = {
            'AccountID': '0',
            'AssignedResourceID': '29682885',
            'AssignedResourceRoleID': '29683436',
            'ChangeApprovalType': '1',
            'CreateDate': '2018-02-20T01:42:57.017',
            'CreatorResourceID': '29683993',
            'DueDateTime': '2018-02-21T01:38:00',
            'ExternalID': None,
            'LastActivityDate': '2018-02-28T04:16:06.297',
            'LastCustomerVisibleActivityDateTime': '2018-02-28T04:16:04.797',
            'Priority': '1',
            'PurchaseOrderNumber': None,
            'Resolution': None,
            'Status': '1',
            'TicketCategory': '3',
            'TicketNumber': 'T20180220.0001',
            'TicketType': '1',
            'Title': 'This is Man test ticket',
            'id': '7872'
        }

        with patch.object(Autotask, '_request', return_value=response_from_autotask) as mock_request:
            entity, status_code = self.autotask_client.query('Ticket', 'id', '1234')

        self.assertDictEqual(entity, expected)
        self.assertEqual(status_code, 200)
        mock_request.assert_called_once_with(
            '<env:Envelope\n    '
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema"\n    '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n    '
            'xmlns:tns="http://autotask.net/ATWS/v1_5/"\n    '
            'xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">\n    '
            '<env:Body>\n        '
            '<tns:query xmlns="http://autotask.net/ATWS/v1_5/">\n            '
            '<sXML>\n                '
            '<![CDATA[<queryxml>\n                  '
            '<entity>Ticket</entity>\n                    '
            '<query>\n                        '
            '<field>id\n                            '
            '<expression op="equals">1234</expression>\n                        '
            '</field>\n                    '
            '</query>\n                '
            '</queryxml>]]>\n            '
            '</sXML>\n        '
            '</tns:query>\n    '
            '</env:Body>\n'
            '</env:Envelope>\n'
        )

    def test_query_with_select_fields_should_return_select_field_belong_to_entity_and_status_code(self):
        response_from_autotask = (
            200,
            self.query_response_for_ticket_entity_as_xml
        )
        expected = {
            'AssignedResourceID': '29682885',
            'id': '7872'
        }

        with patch.object(Autotask, '_request', return_value=response_from_autotask) as mock_request:
            entity, status_code = self.autotask_client.query(
                entity='Ticket',
                filter_field='id',
                filter_value='1234',
                select_fields=('AssignedResourceID', 'id')
            )

        self.assertDictEqual(entity, expected)
        self.assertEqual(status_code, 200)
        mock_request.assert_called_once()

    def test_query_response_status_not_200_should_return_response_text(self):
        response_text = '<?xml version="1.0" encoding="utf-8"?>'
        response_from_autotask = (
            500,
            response_text
        )

        with patch.object(Autotask, '_request', return_value=response_from_autotask) as mock_request:
            entity, status_code = self.autotask_client.query('Ticket', 'id', '1234')

        self.assertEqual(entity, response_text)
        self.assertEqual(status_code, 500)
        mock_request.assert_called_once()

    def test_get_zone_info_should_return_tuple_of_raw_body_and_status_code_when_response_status_code_is_not_200(self):
        mock_response = (500, self.empty_response_body)
        expected = (self.empty_response_body, 500)

        with patch.object(Autotask, '_request', return_value=mock_response) as mock_requests:
            actual = self.autotask_client.get_zone_info()

        self.assertTupleEqual(actual, expected)
        mock_requests.assert_called_once_with(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<soap:Envelope '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
            'xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
            '<soap:Body>'
            '<getZoneInfo xmlns="http://autotask.net/ATWS/v1_5/">'
            f'<UserName>{self.username}</UserName>'
            '</getZoneInfo>'
            '</soap:Body>'
            '</soap:Envelope>'
        )

    def test_get_zone_info_should_return_tuple_of_parsed_response_dict_and_status_code_when_response_code_is_200(self):
        mock_response = (
            200,
            '<?xml version="1.0" encoding="utf-8"?>'
            '<soap:Envelope '
            'xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
            '<soap:Body>'
            '<getZoneInfoResponse xmlns="http://autotask.net/ATWS/v1_5/">'
            '<getZoneInfoResult>'
            '<URL>https://webservices2.autotask.net/ATServices/1.5/atws.asmx</URL>'
            '<ErrorCode>0</ErrorCode>'
            '<DataBaseType>Pro</DataBaseType>'
            '<CI>30798</CI>'
            '<WebUrl>https://ww2.autotask.net/</WebUrl>'
            '</getZoneInfoResult>'
            '</getZoneInfoResponse>'
            '</soap:Body>'
            '</soap:Envelope>'
        )
        expected = (
            OrderedDict([
                ('URL', 'https://webservices2.autotask.net/ATServices/1.5/atws.asmx'),
                ('ErrorCode', '0'),
                ('DataBaseType', 'Pro'),
                ('CI', '30798'),
                ('WebUrl', 'https://ww2.autotask.net/')
            ]),
            200
        )

        with patch.object(Autotask, '_request', return_value=mock_response) as mock_requests:
            actual = self.autotask_client.get_zone_info()

        self.assertTupleEqual(actual, expected)
        mock_requests.assert_called_once()

    def test_get_zone_info_should_set_client_url_to_new_zone_url_when_response_code_is_200(self):
        zone_url = 'new-zone-url'
        mock_response = (
            200,
            '<?xml version="1.0" encoding="utf-8"?>'
            '<soap:Envelope '
            'xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
            '<soap:Body>'
            '<getZoneInfoResponse xmlns="http://autotask.net/ATWS/v1_5/">'
            '<getZoneInfoResult>'
            f'<URL>{zone_url}</URL>'
            '<ErrorCode>0</ErrorCode>'
            '<DataBaseType>Pro</DataBaseType>'
            '<CI>30798</CI>'
            '<WebUrl>https://ww2.autotask.net/</WebUrl>'
            '</getZoneInfoResult>'
            '</getZoneInfoResponse>'
            '</soap:Body>'
            '</soap:Envelope>'
        )

        with patch.object(Autotask, '_request', return_value=mock_response) as mock_requests:
            self.autotask_client.get_zone_info()

        self.assertEqual(self.autotask_client.url, zone_url)
        mock_requests.assert_called_once()
