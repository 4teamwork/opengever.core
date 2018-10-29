from ftw.testbrowser import restapi
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.journal.tests.utils import get_journal_entry
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter


class TestCheckoutAPI(IntegrationTestCase):

    @restapi
    def test_checkout_document(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.document, endpoint='@checkout', method='POST')
        self.assertEqual(204, api_client.status_code)
        self.assertTrue(self.document.is_checked_out())

    @restapi
    def test_checkout_checkedout_document_returns_forbidden(self, api_client):
        self.login(self.regular_user, api_client)
        getMultiAdapter((self.document, self.request), ICheckinCheckoutManager).checkout()
        with api_client.expect_http_error(code=403, reason='Forbidden'):
            api_client.open(self.document, endpoint='@checkout', method='POST')
        expected_error = {u'error': {u'message': u'Checkout is not allowed.', u'type': u'Forbidden'}}
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_checkin_document(self, api_client):
        self.login(self.regular_user, api_client)
        getMultiAdapter((self.document, self.request), ICheckinCheckoutManager).checkout()
        api_client.open(self.document, endpoint='@checkin', method='POST')
        self.assertEqual(204, api_client.status_code)
        self.assertFalse(self.document.is_checked_out())

    @restapi
    def test_checkin_document_with_comment(self, api_client):
        self.login(self.regular_user, api_client)
        getMultiAdapter((self.document, self.request), ICheckinCheckoutManager).checkout()
        api_client.open(self.document, endpoint='@checkin', data={'comment': 'foo bar'})
        self.assertEqual(204, api_client.status_code)
        self.assertFalse(self.document.is_checked_out())
        self.assertEqual('foo bar', get_journal_entry(self.document)['comments'])

    @restapi
    def test_checkin_checkedin_document_returns_forbidden(self, api_client):
        self.login(self.regular_user, api_client)
        with api_client.expect_http_error(code=403, reason='Forbidden'):
            api_client.open(self.document, endpoint='@checkin', method='POST')
        expected_error = {u'error': {u'message': u'Checkin is not allowed.', u'type': u'Forbidden'}}
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_cancel_checkout(self, api_client):
        self.login(self.regular_user, api_client)
        getMultiAdapter((self.document, self.request), ICheckinCheckoutManager).checkout()
        api_client.open(self.document, endpoint='@cancelcheckout', method='POST')
        self.assertEqual(204, api_client.status_code)
        self.assertFalse(self.document.is_checked_out())

    @restapi
    def test_cancel_checkedin_document_returns_forbidden(self, api_client):
        self.login(self.regular_user, api_client)
        with api_client.expect_http_error(code=403, reason='Forbidden'):
            api_client.open(self.document, endpoint='@cancelcheckout', method='POST')
        expected_error = {u'error': {u'message': u'Cancel checkout is not allowed.', u'type': u'Forbidden'}}
        self.assertEqual(expected_error, api_client.contents)
