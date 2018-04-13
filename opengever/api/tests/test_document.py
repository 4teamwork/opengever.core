from ftw.testbrowser import browsing
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter


class TestDocumentPatch(IntegrationTestCase):

    def setUp(self):
        super(TestDocumentPatch, self).setUp()

    @browsing
    def test_document_patch_forbidden_if_not_checked_out(self, browser):
        self.login(self.administrator, browser)
        self.assertFalse(self.document.is_checked_out())
        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(
                self.document.absolute_url(),
                data='{"file": {"data": "foo bar", "filename": "foo.txt",'
                     ' "content-type": "text/plain"}}',
                method='PATCH',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'})
        self.assertEqual(
            browser.json['error']['message'],
            'Document not checked-out by current user.')

    @browsing
    def test_document_patch_forbidden_if_not_checked_out_by_current_user(self, browser):
        self.login(self.regular_user, browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()

        self.login(self.administrator, browser)
        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(
                self.document.absolute_url(),
                data='{"file": {"data": "foo bar", "filename": "foo.txt",'
                     ' "content-type": "text/plain"}}',
                method='PATCH',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'})
        self.assertEqual(
            browser.json['error']['message'],
            'Document not checked-out by current user.')

    @browsing
    def test_document_patch_allowed_if_checked_out_by_current_user(self, browser):
        self.login(self.administrator, browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()
        browser.open(
            self.document.absolute_url(),
            data='{"file": {"data": "foo bar", "filename": "foo.txt",'
                 ' "content-type": "text/plain"}}',
            method='PATCH',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})
        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.document.file.data, 'foo bar')

    @browsing
    def test_document_patch_allowed_if_not_modifying_file(self, browser):
        self.login(self.administrator, browser)
        browser.open(
            self.document.absolute_url(),
            data='{"description": "Foo bar"}',
            method='PATCH',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})
        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.document.Description(), u'Foo bar')
