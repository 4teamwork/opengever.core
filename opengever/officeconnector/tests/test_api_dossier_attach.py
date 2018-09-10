from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.officeconnector.testing import FREEZE_DATE
from opengever.officeconnector.testing import JWT_SIGNING_SECRET_PLONE
from opengever.officeconnector.testing import OCIntegrationTestCase
import jwt


class TestOfficeconnectorDossierAPIWithAttach(OCIntegrationTestCase):

    features = (
        '!officeconnector-checkout',
        'officeconnector-attach',
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

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'documents': [u'createtreatydossiers000000000002'],
            u'exp': 4121033100,
            u'sub': u'kathi.barfuss',
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE)
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

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_attach_oc_url(browser, self.inactive_document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'documents': [u'createinactivedossier00000000002'],
            u'exp': 4121033100,
            u'sub': u'kathi.barfuss',
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE)
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'content-type': u'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-6/document-28',
            u'download': u'download',
            u'filename': u'Uebersicht der Inaktiven Vertraege von 2016.xlsx',
            u'title': u'\xdcbersicht der Inaktiven Vertr\xe4ge von 2016',
            u'uuid': u'createinactivedossier00000000002',
            }]
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        self.assertEqual(payloads, expected_payloads)

        file_contents = self.download_document(browser, raw_token, payloads[0])
        self.assertEquals(file_contents, self.inactive_document.file.data)

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

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_attach_oc_url(browser, self.expired_document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'documents': [u'createexpireddossier000000000002'],
            u'exp': 4121033100,
            u'sub': u'kathi.barfuss',
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE)
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'content-type': u'application/msword',
            u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-5/document-27',
            u'download': u'download',
            u'filename': u'Uebersicht der Vertraege vor 2000.doc',
            u'title': u'\xdcbersicht der Vertr\xe4ge vor 2000',
            u'uuid': u'createexpireddossier000000000002',
            }]
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        self.assertEqual(payloads, expected_payloads)

        file_contents = self.download_document(browser, raw_token, payloads[0])
        self.assertEquals(file_contents, self.expired_document.file.data)

    @browsing
    def test_attach_many_to_email_open(self, browser):
        self.login(self.regular_user, browser)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertTrue(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            self.document,
            self.taskdocument,
            ]

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_dossier_multiattach_oc_url(
                browser,
                self.dossier,
                documents,
                dossier_email,
                )

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'bcc': u'1014013300@example.org',
            u'documents': [u'createtreatydossiers000000000002', u'createtreatydossiers000000000005'],
            u'exp': 4121033100,
            u'sub': u'kathi.barfuss',
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE)
        self.assertEqual(expected_token, token)

        expected_payloads = [
            {
                u'bcc': u'1014013300@example.org',
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                                 u'dossier-1/document-12',
                u'download': u'download',
                u'filename': u'Vertraegsentwurf.docx',
                u'title': u'Vertr\xe4gsentwurf',
                u'uuid': u'createtreatydossiers000000000002',
                },
            {
                u'bcc': u'1014013300@example.org',
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                                 u'dossier-1/task-1/document-13',
                u'download': u'download',
                u'filename': u'Feedback zum Vertragsentwurf.docx',
                u'title': u'Feedback zum Vertragsentwurf',
                u'uuid': u'createtreatydossiers000000000005',
                },
            ]
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)
        self.assertEqual(payloads, expected_payloads)

    @browsing
    def test_attach_many_to_email_inactive(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertFalse(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            self.document,
            self.taskdocument,
            ]

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_dossier_multiattach_oc_url(
                browser,
                self.dossier,
                documents,
                dossier_email,
                )

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'documents': [u'createtreatydossiers000000000002', u'createtreatydossiers000000000005'],
            u'exp': 4121033100,
            u'sub': u'kathi.barfuss',
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE)
        self.assertEqual(expected_token, token)

        expected_payloads = [
            {
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                                 u'dossier-1/document-12',
                u'download': u'download',
                u'filename': u'Vertraegsentwurf.docx',
                u'title': u'Vertr\xe4gsentwurf',
                u'uuid': u'createtreatydossiers000000000002',
                },
            {
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                                 u'dossier-1/task-1/document-13',
                u'download': u'download',
                u'filename': u'Feedback zum Vertragsentwurf.docx',
                u'title': u'Feedback zum Vertragsentwurf',
                u'uuid': u'createtreatydossiers000000000005',
                },
            ]
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)
        self.assertEqual(payloads, expected_payloads)

    @browsing
    def test_attach_many_to_email_resolved(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertFalse(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            self.document,
            self.taskdocument,
            ]

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_dossier_multiattach_oc_url(
                browser,
                self.dossier,
                documents,
                dossier_email,
                )

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'documents': [u'createtreatydossiers000000000002', u'createtreatydossiers000000000005'],
            u'exp': 4121033100,
            u'sub': u'kathi.barfuss',
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE)
        self.assertEqual(expected_token, token)

        expected_payloads = [
            {
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                                 u'dossier-1/document-12',
                u'download': u'download',
                u'filename': u'Vertraegsentwurf.docx',
                u'title': u'Vertr\xe4gsentwurf',
                u'uuid': u'createtreatydossiers000000000002',
                },
            {
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                                 u'dossier-1/task-1/document-13',
                u'download': u'download',
                u'filename': u'Feedback zum Vertragsentwurf.docx',
                u'title': u'Feedback zum Vertragsentwurf',
                u'uuid': u'createtreatydossiers000000000005',
                },
            ]
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)
        self.assertEqual(payloads, expected_payloads)

    @browsing
    def test_checkout_checkin_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(404):
            oc_url = self.fetch_document_checkout_oc_url(browser, self.empty_document)
            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

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
