from ftw.testbrowser import browsing
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_OWNER_ID_KEY
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_SOURCE_UUID_KEY
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_SOURCE_VERSION_KEY
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_STATUS_KEY
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_TOKEN_KEY
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
import json


class TestSaveDocumentAsPdfPost(IntegrationTestCase):

    features = ('bumblebee', )

    @browsing
    def test_save_document_as_pdf_post(self, browser):
        self.login(self.regular_user, browser=browser)
        Versioner(self.document).create_version('Initial version')
        with self.observe_children(self.empty_dossier) as children:
            browser.open(self.empty_dossier, view='@save-document-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"document_uid": self.document.UID()}))
        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()

        self.assertTrue(created_document.is_shadow_document())
        related_items = IRelatedDocuments(created_document).relatedItems
        self.assertEqual(len(related_items), 1)
        self.assertEqual(related_items[0].to_object, self.document)
        annotations = IAnnotations(created_document)
        self.assertEqual(IUUID(self.document),
                         annotations.get(PDF_SAVE_SOURCE_UUID_KEY))
        self.assertEqual('conversion-demanded',
                         annotations.get(PDF_SAVE_STATUS_KEY))
        self.assertIsNotNone(annotations.get(PDF_SAVE_TOKEN_KEY))
        self.assertEqual(self.regular_user.getId(),
                         annotations.get(PDF_SAVE_OWNER_ID_KEY))

        self.assertEqual(browser.status_code, 201)
        self.assertEqual(created_document.absolute_url(), browser.headers['location'])

    @browsing
    def test_save_document_as_pdf_post_without_document_uid_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.empty_dossier, view='@save-document-as-pdf', method='POST',
                         headers=self.api_headers)

        self.assertEqual({
          "message": "Property 'document_uid' is required and should be a UID of a document",
          "type": "BadRequest"}, browser.json)

    @browsing
    def test_save_document_as_pdf_post_with_invalid_document_uid_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.empty_dossier, view='@save-document-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"document_uid": self.task.UID()}))

        self.assertEqual({
          "message": "Property 'document_uid' is required and should be a UID of a document",
          "type": "BadRequest"}, browser.json)

    @browsing
    def test_save_document_as_pdf_post_is_available_for_mails(self, browser):
        self.login(self.regular_user, browser)
        with self.observe_children(self.empty_dossier) as children:
            browser.open(self.empty_dossier, view='@save-document-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"document_uid": self.mail_eml.UID()}))

        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()
        self.assertEqual(browser.status_code, 201)
        self.assertEqual(created_document.absolute_url(), browser.headers['location'])

    @browsing
    def test_save_document_as_pdf_post_is_available_for_workspaces(self, browser):
        self.login(self.workspace_member, browser)
        with self.observe_children(self.workspace) as children:
            browser.open(self.workspace, view='@save-document-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"document_uid": self.workspace_document.UID()}))

        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()
        self.assertEqual(browser.status_code, 201)
        self.assertEqual(created_document.absolute_url(), browser.headers['location'])

    @browsing
    def test_save_document_as_pdf_post_is_available_for_workspace_folders(self, browser):
        self.login(self.workspace_member, browser)
        with self.observe_children(self.workspace_folder) as children:
            browser.open(self.workspace_folder, view='@save-document-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"document_uid": self.workspace_document.UID()}))

        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()
        self.assertEqual(browser.status_code, 201)
        self.assertEqual(created_document.absolute_url(), browser.headers['location'])

    @browsing
    def test_save_document_as_pdf_post_with_invalid_version_id_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.empty_dossier, view='@save-document-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"document_uid": self.document.UID(),
                                          "version_id": "invalid"}))

        self.assertEqual({"message": "Property 'version_id' should be an integer.",
                          "type": "BadRequest"}, browser.json)

    @browsing
    def test_save_document_as_pdf_post_asserts_version_is_convertable(self, browser):
        self.login(self.regular_user, browser)
        self.document.file.filename = u"test.wav"
        self.document.file.contentType = "audio/wav"
        Versioner(self.document).create_version("")

        self.document.file.filename = u"test.txt"
        self.document.file.contentType = "text/plain"
        Versioner(self.document).create_version("")

        browser.open(self.empty_dossier, view='@save-document-as-pdf', method='POST',
                     headers=self.api_headers,
                     data=json.dumps({"document_uid": self.document.UID(),
                                      "version_id": 1}))
        self.assertEqual(browser.status_code, 201)

        with browser.expect_http_error(400):
            browser.open(self.empty_dossier, view='@save-document-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"document_uid": self.document.UID(),
                                          "version_id": 0}))

        self.assertEqual({"message": "This document is not convertable.",
                          "type": "BadRequest"}, browser.json)

    @browsing
    def test_save_document_as_pdf_post_is_not_allowed_if_document_is_checked_out(self, browser):
        self.login(self.regular_user, browser)
        Versioner(self.document).create_version('Initial version')

        manager = getMultiAdapter((self.document, self.request), ICheckinCheckoutManager)
        manager.checkout()

        with browser.expect_http_error(400):
            browser.open(self.empty_dossier, view='@save-document-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"document_uid": self.document.UID()}))

        self.assertEqual({"message": "This document is not convertable.",
                          "type": "BadRequest"}, browser.json)

    @browsing
    def test_save_document_as_pdf_post_handles_retrieving_initial_version(self, browser):
        self.login(self.regular_user, browser)
        self.document.file.filename = u"test.txt"
        self.document.file.contentType = "text/plain"

        # when the initial version does not yet exist, retrieving version 0
        # is handled and returns the pdf for the current state of the document
        with self.observe_children(self.empty_dossier) as children:
            browser.open(self.empty_dossier, view='@save-document-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"document_uid": self.document.UID(),
                                          "version_id": 0}))

        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()
        self.assertIsNone(IAnnotations(created_document).get(PDF_SAVE_SOURCE_VERSION_KEY))

        # Once the initial version has been created, we can retrieve version 0
        Versioner(self.document).create_version("")
        with self.observe_children(self.empty_dossier) as children:
            browser.open(self.empty_dossier, view='@save-document-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"document_uid": self.document.UID(),
                                          "version_id": 0}))

        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()
        self.assertEqual(0, IAnnotations(created_document).get(PDF_SAVE_SOURCE_VERSION_KEY))
