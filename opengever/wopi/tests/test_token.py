from ftw.testing import MockTestCase
from plone.keyring.interfaces import IKeyManager
from opengever.wopi.token import create_access_token
from opengever.wopi.token import validate_access_token
from time import time


class MockKeyManager:
    def secret(self):
        return 'SECRET'


class TestWOPIToken(MockTestCase):

    def setUp(self):
        super(TestWOPIToken, self).setUp()
        self.mock_utility(MockKeyManager(), IKeyManager)

    def test_create_access_token_returns_bytes(self):
        token = create_access_token('john', 'e9d9ab51aecb40b4aa475a0e482f4d74')
        self.assertTrue(isinstance(token, bytes))

    def test_validate_token_returns_none_for_invalid_token(self):
        self.assertEqual(validate_access_token('FAKE TOKEN', 'scope'), None)

    def test_validate_token_returns_none_for_wrong_scope(self):
        token = create_access_token('john', 'e9d9ab51aecb40b4aa475a0e482f4d74')
        self.assertEqual(validate_access_token(token, 'wrong scope'), None)

    def test_validate_token_returns_userid_for_valid_token(self):
        token = create_access_token('john', 'e9d9ab51aecb40b4aa475a0e482f4d74')
        self.assertEqual(
            validate_access_token(token, 'e9d9ab51aecb40b4aa475a0e482f4d74'),
            'john')

    def test_validate_expired_token_returns_none(self):
        timestamp = int(time()) - 43201
        token = create_access_token(
            'john', 'e9d9ab51aecb40b4aa475a0e482f4d74', timestamp=timestamp)
        self.assertEqual(
            validate_access_token(token, 'e9d9ab51aecb40b4aa475a0e482f4d74'),
            None)

    def test_validate_token_with_invalid_timestamp_returns_none(self):
        token = 'd' * 32 + 't' * 8 + 'userid'
        self.assertEqual(validate_access_token(token, 'scope'), None)