from ftw.testbrowser import browsing
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.journal.tests.utils import get_journal_entry
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter


class TestCheckoutAPI(IntegrationTestCase):

    def setUp(self):
        super(TestCheckoutAPI, self).setUp()

    @browsing
    def test_checkout_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document.absolute_url() + '/@checkout',
                     method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(204, browser.status_code)
        self.assertTrue(self.document.is_checked_out())

    @browsing
    def test_checkout_checkedout_document_returns_forbidden(self, browser):
        self.login(self.regular_user, browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()

        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(self.document.absolute_url() + '/@checkout',
                         method='POST', headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'type': u'Forbidden',
             u'additional_metadata': {},
             u'translated_message': u'Checkout is not allowed.',
             u'message': u'msg_checkout_disallowed'},
            browser.json)

    @browsing
    def test_checkin_document(self, browser):
        self.login(self.regular_user, browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()

        browser.open(self.document.absolute_url() + '/@checkin',
                     method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(204, browser.status_code)
        self.assertFalse(self.document.is_checked_out())

    @browsing
    def test_checkin_document_with_comment(self, browser):
        self.login(self.regular_user, browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()

        browser.open(self.document.absolute_url() + '/@checkin',
                     data='{"comment": "foo bar"}',
                     method='POST',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})
        self.assertEqual(204, browser.status_code)
        self.assertFalse(self.document.is_checked_out())

        self.assertEqual(
            'foo bar', get_journal_entry(self.document)['comments'])

    @browsing
    def test_checkin_checkedin_document_returns_forbidden(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(self.document.absolute_url() + '/@checkin',
                         method='POST', headers={'Accept': 'application/json'})
        self.assertIn('Checkin is not allowed', browser.contents)

    @browsing
    def test_cancel_checkout(self, browser):
        self.login(self.regular_user, browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()

        browser.open(self.document.absolute_url() + '/@cancelcheckout',
                     method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(204, browser.status_code)
        self.assertFalse(self.document.is_checked_out())

    @browsing
    def test_cancel_checkedin_document_returns_forbidden(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(self.document.absolute_url() + '/@cancelcheckout',
                         method='POST', headers={'Accept': 'application/json'})
        self.assertIn('Cancel checkout is not allowed', browser.contents)
