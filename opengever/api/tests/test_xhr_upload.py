from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from requests_toolbelt.multipart.encoder import MultipartEncoder
from zExceptions import BadRequest


class TestXHRUpload(IntegrationTestCase):

    def prepare_request(self, fields):
        encoder = MultipartEncoder(fields=fields)
        return encoder.to_string(), {
            'Content-Type': encoder.content_type,
            'Accept': 'application/json',
        }

    @browsing
    def test_create_document(self, browser):
        fields = {
            'title': 'My document',
            'file': ('mydocument.txt', 'my text', 'text/plain'),
        }

        self.login(self.regular_user, browser)
        body, headers = self.prepare_request(fields)

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier.absolute_url() + '/@xhr-upload',
                         method='POST',
                         headers=headers,
                         data=body)

        self.assertEqual(201, browser.status_code)

        doc = children["added"].pop()
        self.assertEqual('My document', doc.Title())
        self.assertFalse(doc.is_mail)

    @browsing
    def test_create_document_without_title_will_use_file_name_as_title(self, browser):
        fields = {
            'file': ('mydocument.txt', 'my text', 'text/plain'),
        }

        self.login(self.regular_user, browser)
        body, headers = self.prepare_request(fields)

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier.absolute_url() + '/@xhr-upload',
                         method='POST',
                         headers=headers,
                         data=body)

        self.assertEqual(201, browser.status_code)

        doc = children["added"].pop()
        self.assertEqual('mydocument', doc.Title())

    @browsing
    def test_create_document_without_file_will_raise_bad_request(self, browser):
        fields = {
            'title': 'My document',
        }

        self.login(self.regular_user, browser)
        body, headers = self.prepare_request(fields)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(self.dossier.absolute_url() + '/@xhr-upload',
                         method='POST',
                         headers=headers,
                         data=body)

        self.assertEqual('Property "file" is required',
                         str(cm.exception))

    @browsing
    def test_create_email(self, browser):
        fields = {
            'title': 'My E-Mail',
            'file': ('mymail.eml', 'my text', 'text/plain'),
        }

        self.login(self.regular_user, browser)
        body, headers = self.prepare_request(fields)

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier.absolute_url() + '/@xhr-upload',
                         method='POST',
                         headers=headers,
                         data=body)

        self.assertEqual(201, browser.status_code)

        mail = children["added"].pop()
        self.assertEqual('My E-Mail', mail.Title())
        self.assertTrue(mail.is_mail)
