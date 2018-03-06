from unittest.mock import Mock


class TestHelper(object):
    @staticmethod
    def mock_response(status_code=200, body=None, headers=None):
        return Mock(
            headers=headers,
            status_code=status_code,
            json=Mock(return_value=body),
            text=body
        )
