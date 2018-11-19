from ftw.testbrowser import restapi
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrashable
from opengever.trash.trash import ITrashed


class TestTrashAPI(IntegrationTestCase):

    @restapi
    def test_trash_document(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.document, endpoint='@trash', method='POST')
        self.assertEqual(204, api_client.status_code)
        self.assertTrue(ITrashed.providedBy(self.document))

    @restapi
    def test_trash_trashed_document_gives_bad_request(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.document, endpoint='@trash', method='POST')

        with api_client.expect_http_error(code=400, reason='Bad Request'):
            api_client.open(self.document, endpoint='@trash', method='POST')

        self.assertEqual(u'Already trashed', api_client.contents[u'error'][u'message'])

    @restapi
    def test_trash_checked_out_document_gives_bad_request(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.document, endpoint='@checkout', method='POST')

        with api_client.expect_http_error(code=400, reason='Bad Request'):
            api_client.open(self.document, endpoint='@trash', method='POST')

        self.assertEqual(u'Can not trash a checked-out document', api_client.contents[u'error'][u'message'])

    @restapi
    def test_trash_document_without_permission_gives_401(self, api_client):
        self.login(self.regular_user, api_client)
        self.document.aq_parent.manage_permission('opengever.trash: Trash content', roles=[], acquire=0)
        with api_client.expect_http_error(code=401, reason='Unauthorized'):
            api_client.open(self.document, endpoint='@trash', method='POST')

        self.assertEqual(u'You are not authorized to access this resource.', api_client.contents[u'message'])

    @restapi
    def test_untrash_document(self, api_client):
        self.login(self.regular_user, api_client)
        trasher = ITrashable(self.document)
        trasher.trash()
        api_client.open(self.document, endpoint='@untrash', method='POST')
        self.assertEqual(204, api_client.status_code)
        self.assertFalse(ITrashed.providedBy(self.document))

    @restapi
    def test_untrash_document_without_permission_gives_401(self, api_client):
        self.login(self.regular_user, api_client)
        self.document.aq_parent.manage_permission('opengever.trash: Untrash content', roles=[], acquire=0)
        with api_client.expect_http_error(code=401, reason='Unauthorized'):
            api_client.open(self.document, endpoint='@untrash', method='POST')

        self.assertEqual(u'You are not authorized to access this resource.', api_client.contents[u'message'])
