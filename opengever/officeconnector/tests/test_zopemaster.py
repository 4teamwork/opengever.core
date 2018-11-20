from ftw.testbrowser import browsing
from ftw.testing import freeze
from hashlib import sha256
from opengever.officeconnector.testing import FREEZE_DATE
from opengever.officeconnector.testing import JWT_SIGNING_SECRET_ZOPE
from opengever.officeconnector.testing import OCIntegrationTestCase
from opengever.testing.assets import path_to_asset
import jwt


class TestOfficeconnectorAsZopemasterDossierAPIWithAttach(OCIntegrationTestCase):
    features = (
        'officeconnector-attach',
    )

    @browsing
    def test_attach_to_email_open_with_file(self, browser):
        self.login(self.manager, browser)

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'documents': [u'createtreatydossiers000000000002'],
            u'exp': 4121033100,
            u'sub': u'admin',
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_ZOPE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'bcc': u'1014013300@example.org',
            u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-12',
            u'download': u'download',
            u'filename': u'Vertraegsentwurf.docx',
            u'title': u'Vertr\xe4gsentwurf',
            u'uuid': u'createtreatydossiers000000000002',
            }]
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        self.assertEqual(payloads, expected_payloads)

        file_contents = self.download_document(browser, raw_token, payloads[0])
        self.assertEquals(file_contents, self.document.file.data)


class TestOfficeconnectorAsZopemasterDossierAPIWithCheckout(OCIntegrationTestCase):
    features = (
        'officeconnector-checkout',
    )

    @browsing
    def test_checkout_checkin_open_with_file_without_comment(self, browser):
        self.login(self.manager, browser)

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_checkout_oc_url(browser, self.document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'checkout',
            u'documents': [u'createtreatydossiers000000000002'],
            u'exp': 4121033100,
            u'sub': u'admin',
            u'url': u'http://nohost/plone/oc_checkout',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_ZOPE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'checkin-with-comment': u'@@checkin_document',
            u'checkin-without-comment': u'checkin_without_comment',
            u'checkout': u'@@checkout_documents',
            u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-12',
            u'download': u'download',
            u'filename': u'Vertraegsentwurf.docx',
            u'upload-form': u'file_upload',
            u'uuid': u'createtreatydossiers000000000002',
            }]
        payloads = self.fetch_document_checkout_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        for payload, expected_payload in zip(payloads, expected_payloads):
            self.assertTrue(payload.get('csrf-token'))
            self.assertDictContainsSubset(expected_payload, payload)

        self.checkout_document(browser, raw_token, payloads[0], self.document)

        lock_token = self.lock_document(browser, raw_token, self.document)

        original_checksum = sha256(
            self.download_document(browser, raw_token, payloads[0]),
            ).hexdigest()

        with open(path_to_asset('addendum.docx')) as f:
            self.upload_document(browser, raw_token, payloads[0], self.document, f)

        new_checksum = sha256(
            self.download_document(browser, raw_token, payloads[0]),
            ).hexdigest()

        self.assertNotEquals(new_checksum, original_checksum)

        self.unlock_document(browser, raw_token, self.document, lock_token)

        self.checkin_document(browser, raw_token, payloads[0], self.document)
