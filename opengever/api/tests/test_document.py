from ftw.testbrowser import browsing
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter


class TestDocumentSerializer(IntegrationTestCase):

    @browsing
    def test_document_serialization_contains_preview_url(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'preview_url')[:124],
            u'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local/51d6317494e'
            u'ccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2/preview')

    @browsing
    def test_document_serialization_contains_pdf_url(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'pdf_url')[:120],
            u'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local/51d6317494e'
            u'ccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2/pdf')

    @browsing
    def test_document_serialization_contains_thumbnail_url(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'thumbnail_url')[:126],
            u'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local/51d6317494e'
            u'ccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2/thumbnail')

    @browsing
    def test_document_serialization_contains_file_extension(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual('.docx', browser.json.get(u'file_extension'))

        browser.open(self.mail_msg, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual('.msg', browser.json.get(u'file_extension'))


class TestDocumentPatch(IntegrationTestCase):

    def setUp(self):
        super(TestDocumentPatch, self).setUp()

    @browsing
    def test_document_patch_forbidden_if_not_checked_out(self, browser):
        self.login(self.regular_user, browser)
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
        self.login(self.dossier_responsible, browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()

        self.login(self.regular_user, browser)
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
        self.login(self.regular_user, browser)
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
        self.login(self.regular_user, browser)
        browser.open(
            self.document.absolute_url(),
            data='{"description": "Foo bar"}',
            method='PATCH',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})
        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.document.Description(), u'Foo bar')
