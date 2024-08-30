from opengever.document.versioner import Versioner
from opengever.sign.token import InvalidToken
from opengever.sign.token import TokenManager
from opengever.testing import IntegrationTestCase


class TestTokenManager(IntegrationTestCase):
    def test_can_issue_a_valid_token(self):
        self.login(self.regular_user)
        manager = TokenManager(self.document)
        manager.validate_token(manager.issue_token())

    def test_issued_token_is_only_valid_for_a_specific_document(self):
        self.login(self.regular_user)
        token = TokenManager(self.document).issue_token()
        with self.assertRaises(InvalidToken):
            TokenManager(self.subdocument).validate_token(token)

    def test_issued_token_is_only_valid_for_a_specific_document_version(self):
        self.login(self.regular_user)
        manager = TokenManager(self.document)
        token = manager.issue_token()

        self.assertTrue(manager.validate_token(token))

        Versioner(self.document).create_version('new version')
        with self.assertRaises(InvalidToken):
            manager.validate_token(token)

    def test_can_invalidate_the_current_token(self):
        self.login(self.regular_user)
        manager = TokenManager(self.document)
        token = manager.issue_token()

        self.assertTrue(manager.validate_token(token))

        manager.invalidate_token()
        with self.assertRaises(InvalidToken):
            manager.validate_token(token)

    def test_can_validate_a_token_without_permission(self):
        with self.login(self.regular_user):
            manager = TokenManager(self.document)
            token = manager.issue_token()

        self.assertTrue(manager.validate_token(token))
