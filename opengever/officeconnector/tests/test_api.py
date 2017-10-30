from ftw.testbrowser import browsing
from opengever.document.document import Document
from opengever.officeconnector.testing import OCIntegrationTestCase


class TestOfficeconnectorAPI(OCIntegrationTestCase):
    @browsing
    def test_attach_to_email(self, browser):
        self.login(self.regular_user, browser)

        # Open dossier
        # Document with file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Inactive dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document with file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Resolved dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document with file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

    @browsing
    def test_attach_many_to_email(self, browser):
        self.login(self.regular_user, browser)

        # Open Dossier
        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)
        self.assertTrue(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        oc_url = self.fetch_dossier_multiattach_oc_url(browser, self.dossier, documents, dossier_email)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Inactive dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)
        self.assertTrue(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        oc_url = self.fetch_dossier_multiattach_oc_url(browser, self.dossier, documents, dossier_email)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Resolved dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)
        self.assertTrue(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        oc_url = self.fetch_dossier_multiattach_oc_url(browser, self.dossier, documents, dossier_email)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

    @browsing
    def test_checkout_checkin(self, browser):
        self.login(self.regular_user, browser)

        # Open dossier
        # Document with file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Inactive dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document with file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Resolved dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document with file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)


class TestOfficeconnectorAPIWithAttach(OCIntegrationTestCase):
    features = (
        'officeconnector-attach',
    )

    @browsing
    def test_attach_to_email(self, browser):
        self.login(self.regular_user, browser)

        # Open dossier
        # Document with file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Inactive dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document with file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Resolved dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document with file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

    @browsing
    def test_attach_many_to_email(self, browser):
        self.login(self.regular_user, browser)

        # Open Dossier
        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)
        self.assertTrue(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        oc_url = self.fetch_dossier_multiattach_oc_url(browser, self.dossier, documents, dossier_email)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Inactive dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)
        self.assertTrue(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        oc_url = self.fetch_dossier_multiattach_oc_url(browser, self.dossier, documents, dossier_email)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Resolved dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)
        self.assertTrue(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        oc_url = self.fetch_dossier_multiattach_oc_url(browser, self.dossier, documents, dossier_email)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

    @browsing
    def test_checkout_checkin(self, browser):
        self.login(self.regular_user, browser)

        # Open dossier
        # Document with file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Inactive dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document with file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Resolved dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document with file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)


class TestOfficeconnectorAPIWithCheckout(OCIntegrationTestCase):
    features = (
        'officeconnector-checkout',
    )

    @browsing
    def test_attach_to_email(self, browser):
        self.login(self.regular_user, browser)

        # Open dossier
        # Document with file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Inactive dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document with file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Resolved dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document with file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_attach_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

    @browsing
    def test_attach_many_to_email(self, browser):
        self.login(self.regular_user, browser)

        # Open Dossier
        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)
        self.assertTrue(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        oc_url = self.fetch_dossier_multiattach_oc_url(browser, self.dossier, documents, dossier_email)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Inactive dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)
        self.assertTrue(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        oc_url = self.fetch_dossier_multiattach_oc_url(browser, self.dossier, documents, dossier_email)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Resolved dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)
        self.assertTrue(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            doc for doc
            in self.dossier.objectValues()
            if isinstance(doc, Document)
            if doc.file
            ]

        oc_url = self.fetch_dossier_multiattach_oc_url(browser, self.dossier, documents, dossier_email)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

    @browsing
    def test_checkout_checkin(self, browser):
        self.login(self.regular_user, browser)

        # Open dossier
        # Document with file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document)
        self.assertTrue(oc_url)
        self.assertEquals(200, browser.status_code)

        raw_token, token = self.validate_checkout_token(oc_url)
        payloads = self.fetch_document_checkout_payloads(browser, token)
        for payload in payloads:
            self.validate_checkout_payload(payload, self.document)
            self.checkout_document(browser, raw_token, payload, self.document)
            lock_token = self.lock_document(browser, raw_token, self.document)
            old_file_contents = self.download_document(browser, raw_token, payload, self.document)
            self.unlock_document(browser, raw_token, self.document, lock_token)
            with open('../../opengever/testing/assets/addendum_nova.docx', 'rb') as f:
                self.upload_document(browser, raw_token, payload, self.document, f)
            new_file_contents = self.download_document(browser, raw_token, payload, self.document)
            self.assertNotEquals(new_file_contents, old_file_contents)
            # Upload
            # Unlock
            # Check in
            # Check out
            # Check in with a comment

        # Document without file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Inactive dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document with file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Resolved dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document with file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)

        # Document without file
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document_without_file)
        self.assertIsNone(oc_url)
        self.assertEquals(404, browser.status_code)


class TestOfficeconnectorAPIWithOAW(OCIntegrationTestCase):
    pass
