from ftw.testbrowser import restapi
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter


class TestDocumentPatch(IntegrationTestCase):

    @restapi
    def test_document_patch_forbidden_if_not_checked_out(self, api_client):
        self.login(self.regular_user, api_client)
        self.assertFalse(self.document.is_checked_out())
        payload = {"file": {"data": "foo bar", "filename": "foo.txt", "content-type": "text/plain"}}
        with api_client.expect_http_error(code=403, reason='Forbidden'):
            api_client.open(self.document, data=payload, method='PATCH')
        self.assertEqual('Document not checked-out by current user.', api_client.contents['error']['message'])

    @restapi
    def test_document_patch_forbidden_if_not_checked_out_by_current_user(self, api_client):
        self.login(self.dossier_responsible, api_client)
        getMultiAdapter((self.document, self.request), ICheckinCheckoutManager).checkout()
        self.login(self.regular_user, api_client)
        payload = {"file": {"data": "foo bar", "filename": "foo.txt", "content-type": "text/plain"}}
        with api_client.expect_http_error(code=403, reason='Forbidden'):
            api_client.open(self.document, data=payload, method='PATCH')
        self.assertEqual('Document not checked-out by current user.', api_client.contents['error']['message'])

    @restapi
    def test_document_patch_allowed_if_checked_out_by_current_user(self, api_client):
        self.login(self.regular_user, api_client)
        getMultiAdapter((self.document, self.request), ICheckinCheckoutManager).checkout()
        payload = {"file": {"data": "foo bar", "filename": "foo.txt", "content-type": "text/plain"}}
        api_client.open(self.document, data=payload, method='PATCH')
        self.assertEqual(204, api_client.status_code)
        self.assertEqual('foo bar', self.document.file.data)

    @restapi
    def test_document_patch_allowed_if_not_modifying_file(self, api_client):
        self.login(self.regular_user, api_client)
        payload = {"description": "Foo bar"}
        api_client.open(self.document, data=payload, method='PATCH')
        self.assertEqual(204, api_client.status_code)
        self.assertEqual(u'Foo bar', self.document.Description())
