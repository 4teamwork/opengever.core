from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.officeconnector.testing import FREEZE_DATE
from opengever.officeconnector.testing import JWT_SIGNING_SECRET_PLONE
from opengever.officeconnector.testing import OCIntegrationTestCase
import jwt


class TestOfficeconnectorForwardingAPIWithAttach(OCIntegrationTestCase):
    features = (
        'officeconnector-attach',
    )

    @browsing
    def test_attach_to_email_open_without_file(self, browser):
        self.login(self.secretariat_user, browser)
        self.inbox_forwarding_document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(
                browser,
                self.inbox_forwarding_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_open_with_file(self, browser):
        self.login(self.secretariat_user, browser)

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_attach_oc_url(browser, self.inbox_forwarding_document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'documents': [u'createinbox000000000000000000004'],
            u'exp': 4121033100,
            u'sub': u'jurgen.konig',
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE)
        self.assertEqual(token, expected_token)

        expected_payloads = [{
            u'content-type': u'text/plain',
            u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
            u'document-url': u'http://nohost/plone/eingangskorb/forwarding-1/document-11',
            u'download': u'download',
            u'filename': u'Dokument im Eingangskoerbliweiterleitung.txt',
            u'title': u'Dokument im Eingangsk\xf6rbliweiterleitung',
            u'uuid': u'createinbox000000000000000000004',
            }]
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        self.assertEqual(payloads, expected_payloads)

        file_contents = self.download_document(browser, raw_token, payloads[0])
        self.assertEquals(file_contents, self.inbox_forwarding_document.file.data)
