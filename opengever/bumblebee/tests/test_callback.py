from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.tests.helpers import download_token_for
from ftw.testing import freeze
from opengever.bumblebee.browser.callback import StoreArchivalFile
from opengever.document.archival_file import STATE_FAILED_TEMPORARILY
from opengever.document.archival_file import STATE_FAILED_PERMANENTLY
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.testing import FunctionalTestCase
from plone.namedfile.file import NamedBlobFile
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
