from copy import deepcopy
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.testbrowser import browsing
from ftw.testing import freeze
from hashlib import sha256
from opengever.document.document import Document
from opengever.officeconnector.testing import FREEZE_DATE
from opengever.officeconnector.testing import JWT_SIGNING_SECRET_PLONE
from opengever.officeconnector.testing import OCSolrIntegrationTestCase
from opengever.testing.assets import path_to_asset
from zope.annotation.interfaces import IAnnotations
import jwt


class TestOfficeconnectorDossierAPIWithCheckout(OCSolrIntegrationTestCase):

    features = (
        '!officeconnector-attach',
        'officeconnector-checkout',
    )

    @browsing
    def test_attach_to_email_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.empty_document)
            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.inactive_document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.inactive_document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.expired_document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.expired_document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_many_to_email_open(self, browser):
        self.login(self.regular_user, browser)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertTrue(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        with browser.expect_http_error(404):
            oc_url = self.fetch_dossier_multiattach_oc_url(
                browser,
                self.dossier,
                documents,
                dossier_email,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_many_to_email_inactive(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertIsNone(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        with browser.expect_http_error(404):
            oc_url = self.fetch_dossier_multiattach_oc_url(
                browser,
                self.dossier,
                documents,
                dossier_email,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_many_to_email_resolved(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertIsNone(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        with browser.expect_http_error(404):
            oc_url = self.fetch_dossier_multiattach_oc_url(
                browser,
                self.dossier,
                documents,
                dossier_email,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(404):
            oc_url = self.fetch_document_checkout_oc_url(browser, self.empty_document)
            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_open_with_file_without_comment(self, browser):
        self.login(self.regular_user, browser)

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_checkout_oc_url(browser, self.document)

        self.assertIsNotNone(oc_url)
        self.assertEqual(200, browser.status_code)

        expected_token = {
            u'action': u'checkout',
            u'documents': [u'createtreatydossiers000000000002'],
            u'exp': 4121033100,
            u'sub': self.regular_user.id,
            u'url': u'http://nohost/plone/oc_checkout',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'status': u'status',
            u'cancelcheckout': u'@cancelcheckout',
            u'checkin': u'@checkin',
            u'checkout': u'@checkout',
            u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14',
            u'download': u'download',
            u'filename': u'Vertraegsentwurf.docx',
            u'has_pending_changes': False,
            u'lock': u'@lock',
            u'unlock': u'@unlock',
            u'upload': u'@tus-replace',
            u'uuid': u'createtreatydossiers000000000002',
            u'version': None,
            }]
        payloads = self.fetch_document_checkout_payloads(browser, raw_token, token)
        self.assertEqual(200, browser.status_code)

        for payload, expected_payload in zip(payloads, expected_payloads):
            payload_copy = deepcopy(payload)
            self.assertFalse(payload_copy.pop('csrf-token', None))
            self.assertTrue(payload_copy.pop('reauth', None))
            self.assertEqual(expected_payload, payload_copy)

        self.checkout_document(browser, raw_token, payloads[0], self.document)
        lock_token = self.lock_document(
            browser, raw_token, payloads[0], self.document)

        original_checksum = sha256(
            self.download_document(browser, raw_token, payloads[0]),
            ).hexdigest()

        with open(path_to_asset('addendum.docx')) as f:
            self.upload_document(
                browser, raw_token, payloads[0], self.document, f,
                lock_token=lock_token,
            )

        new_checksum = sha256(
            self.download_document(browser, raw_token, payloads[0]),
            ).hexdigest()
        self.assertNotEqual(new_checksum, original_checksum)

        self.unlock_document(browser, raw_token, payloads[0], self.document)
        self.checkin_document(browser, raw_token, payloads[0], self.document)

    @browsing
    def test_checkout_checkin_open_with_file_with_comment(self, browser):
        self.login(self.regular_user, browser)

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_checkout_oc_url(browser, self.document)

        self.assertIsNotNone(oc_url)
        self.assertEqual(200, browser.status_code)

        expected_token = {
            u'action': u'checkout',
            u'documents': [u'createtreatydossiers000000000002'],
            u'exp': 4121033100,
            u'sub': self.regular_user.id,
            u'url': u'http://nohost/plone/oc_checkout',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'status': u'status',
            u'cancelcheckout': u'@cancelcheckout',
            u'checkin': u'@checkin',
            u'checkout': u'@checkout',
            u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14',
            u'download': u'download',
            u'filename': u'Vertraegsentwurf.docx',
            u'has_pending_changes': False,
            u'lock': u'@lock',
            u'unlock': u'@unlock',
            u'upload': u'@tus-replace',
            u'uuid': u'createtreatydossiers000000000002',
            u'version': None,
        }]
        payloads = self.fetch_document_checkout_payloads(browser, raw_token, token)
        self.assertEqual(200, browser.status_code)

        for payload, expected_payload in zip(payloads, expected_payloads):
            payload_copy = deepcopy(payload)
            self.assertFalse(payload_copy.pop('csrf-token', None))
            self.assertTrue(payload_copy.pop('reauth', None))
            self.assertEqual(expected_payload, payload_copy)

        self.checkout_document(browser, raw_token, payloads[0], self.document)
        lock_token = self.lock_document(
            browser, raw_token, payloads[0], self.document)

        original_checksum = sha256(
            self.download_document(browser, raw_token, payloads[0]),
            ).hexdigest()

        with open(path_to_asset('addendum.docx')) as f:
            self.upload_document(
                browser, raw_token, payloads[0], self.document, f,
                lock_token=lock_token,
            )

        new_checksum = sha256(
            self.download_document(browser, raw_token, payloads[0]),
            ).hexdigest()
        self.assertNotEqual(new_checksum, original_checksum)

        self.unlock_document(browser, raw_token, payloads[0], self.document)
        self.checkin_document(
            browser,
            raw_token,
            payloads[0],
            self.document,
            comment='foobar',
            )

        # Verify journal entries produced by the cycle
        journal = IAnnotations(self.document, JOURNAL_ENTRIES_ANNOTATIONS_KEY).get(
            JOURNAL_ENTRIES_ANNOTATIONS_KEY)
        expected_actions = ['Document added',
                            'Document checked out',
                            'File copy downloaded',
                            'File copy downloaded',
                            'Document checked in']
        self.assertEquals(expected_actions,
                          [entry["action"]["type"] for entry in journal])

    @browsing
    def test_checkout_checkin_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.inactive_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.inactive_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.expired_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.expired_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_collaboratively_checked_out_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.get_checkout_manager(self.empty_document).checkout(collaborative=True)

        with browser.expect_http_error(403):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.empty_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_collaboratively_checked_out_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.get_checkout_manager(self.document).checkout(collaborative=True)

        with browser.expect_http_error(403):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)
