from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.tests.helpers import download_token_for
from ftw.bumblebee.tests.helpers import get_download_token
from ftw.testing import freeze
from opengever.bumblebee.browser.callback import StoreArchivalFile
from opengever.bumblebee.browser.callback import ReceiveDocumentPDF
from opengever.document.archival_file import STATE_FAILED_TEMPORARILY
from opengever.document.archival_file import STATE_FAILED_PERMANENTLY
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_TOKEN_KEY
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_STATUS_KEY
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_stream
from plone.namedfile.file import NamedBlobFile
from zExceptions import Unauthorized
from zope.annotation import IAnnotations
from ZPublisher.HTTPRequest import FileUpload
import cgi
import json


class TestStoreArchivalFile(FunctionalTestCase):

    def setUp(self):
        super(TestStoreArchivalFile, self).setUp()
        self.document = create(Builder('document')
                               .titled(u'\xdcberpr\xfcfung XY')
                               .with_dummy_content())

    def test_updates_archival_file_when_conversion_succeeded(self):
        with freeze(datetime(2016, 4, 25, 10, 24)):
            body = {'status': "success",
                    'data': "data:application/pdf;base64,VGVzdCBTdHJpbmc=",
                    'token': download_token_for(self.document)}
            self.request.set('BODY', json.dumps(body))

            view = StoreArchivalFile(self.document, self.request)
            view()

        archival_file = IDocumentMetadata(self.document).archival_file
        self.assertEquals('Ueberpruefung XY.pdf', archival_file.filename)
        self.assertTrue(isinstance(archival_file, NamedBlobFile))
        self.assertEquals('application/pdf', archival_file.contentType)
        self.assertEquals('Test String', archival_file.data)

    def test_sets_failed_permanently_state_when_conversion_was_skipped(self):
        with freeze(datetime(2016, 4, 25, 10, 24)):
            body = {"status": "skipped",
                    "error": "File is password protected.",
                    "token": download_token_for(self.document)}
            self.request.set('BODY', json.dumps(body))

            view = StoreArchivalFile(self.document, self.request)
            view()

        self.assertEquals(
            STATE_FAILED_PERMANENTLY,
            IDocumentMetadata(self.document).archival_file_state)

    def test_sets_failed_temporary_state_when_conversion_has_not_succeeded_or_skipped(self):
        with freeze(datetime(2016, 4, 25, 10, 24)):
            body = {"status": "failed",
                    "error": "Some parts of the document could not be processed",
                    "token": download_token_for(self.document)}
            self.request.set('BODY', json.dumps(body))

            view = StoreArchivalFile(self.document, self.request)
            view()

        self.assertEquals(
            STATE_FAILED_TEMPORARILY,
            IDocumentMetadata(self.document).archival_file_state)


class TestReceiveDocumentPDF(FunctionalTestCase):

    save_token = 'abcd'

    def setUp(self):
        super(TestReceiveDocumentPDF, self).setUp()
        self.document = create(Builder('document')
                               .titled(u'\xdcberpr\xfcfung XY')).as_shadow_document()
        IAnnotations(self.document)[PDF_SAVE_TOKEN_KEY] = self.save_token

    def prepare_request(self):
        fieldstorage = cgi.FieldStorage()
        fieldstorage.file = resource_stream("opengever.bumblebee.tests.assets", "vertragsentwurf.pdf")
        fieldstorage.filename = 'test.pdf'
        file = FileUpload(fieldstorage)
        self.request.set('status', "success")
        self.request.set('pdf', file)
        self.request.set('token', get_download_token())
        self.request.set('opaque_id', self.save_token)
        self.request.method = "POST"

    def test_raises_unathorized_when_pdf_save_token_is_wrong(self):
        IAnnotations(self.document)[PDF_SAVE_TOKEN_KEY] = "wrong token"
        with freeze(datetime(2016, 4, 25, 10, 24)):
            self.prepare_request()
            view = ReceiveDocumentPDF(self.document, self.request)
            with self.assertRaises(Unauthorized):
                view()

    def test_behavior_when_conversion_succeeded(self):
        self.assertFalse(self.document.has_file())
        self.assertIn(PDF_SAVE_TOKEN_KEY, IAnnotations(self.document))
        with freeze(datetime(2016, 4, 25, 10, 24)):
            self.prepare_request()
            view = ReceiveDocumentPDF(self.document, self.request)
            view()

        # File was set and document left the shadow state.
        self.assertTrue(self.document.has_file())
        self.assertFalse(self.document.is_shadow_document())
        # Annotation show successful conversion status and save token was removed.
        self.assertEqual('conversion-successful', IAnnotations(self.document)[PDF_SAVE_STATUS_KEY])
        self.assertNotIn(PDF_SAVE_TOKEN_KEY, IAnnotations(self.document))

    def test_behavior_when_conversion_failed(self):
        self.assertFalse(self.document.has_file())
        self.assertIn(PDF_SAVE_TOKEN_KEY, IAnnotations(self.document))
        with freeze(datetime(2016, 4, 25, 10, 24)):
            self.prepare_request()
            self.request.set('status', "failed")
            view = ReceiveDocumentPDF(self.document, self.request)
            view()

        # File was not set and document still in the shadow state.
        self.assertFalse(self.document.has_file())
        self.assertTrue(self.document.is_shadow_document())
        # Annotation show failed conversion status and save token was not removed.
        self.assertEqual('conversion-failed', IAnnotations(self.document)[PDF_SAVE_STATUS_KEY])
        self.assertIn(PDF_SAVE_TOKEN_KEY, IAnnotations(self.document))

    def test_behavior_when_conversion_skipped(self):
        self.assertFalse(self.document.has_file())
        self.assertIn(PDF_SAVE_TOKEN_KEY, IAnnotations(self.document))
        with freeze(datetime(2016, 4, 25, 10, 24)):
            self.prepare_request()
            self.request.set('status', "skipped")
            view = ReceiveDocumentPDF(self.document, self.request)
            view()

        # File was not set and document still in the shadow state.
        self.assertFalse(self.document.has_file())
        self.assertTrue(self.document.is_shadow_document())
        # Annotation show failed conversion status and save token was not removed.
        self.assertEqual('conversion-skipped', IAnnotations(self.document)[PDF_SAVE_STATUS_KEY])
        self.assertIn(PDF_SAVE_TOKEN_KEY, IAnnotations(self.document))
