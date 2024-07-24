from opengever.document.versioner import Versioner
from opengever.testing import IntegrationTestCase
from opengever.sign.sign import Signer
from zope.annotation import IAnnotations
from opengever.sign.sign import SignStorage
from opengever.sign.client import SignServiceClient
import requests_mock
from ftw.testing import freeze
from plone import api
from os import environ
from opengever.document.document import Document
from datetime import datetime


freezed_now = datetime(2001, 1, 1)

@requests_mock.Mocker()
class TestSigning(IntegrationTestCase):

    def test_signing_document_is_stored_in_the_document_annotations(self, mocker):
        self.login(self.regular_user)

        mocker.post(environ.get('SIGN_SERVICE_URL'), json=[])

        with freeze(freezed_now):
            Signer(self.document).start_signing()

        self.assertEqual(
            [{"userid": self.regular_user.id, 'created':freezed_now, 'state': 'pending'}],
            IAnnotations(self.document).get(SignStorage.key).values()
        )

    def test_signing_document_finalize_document_if_not_alredy_finalized(self, mocker):
        self.login(self.regular_user)

        mocker.post(environ.get('SIGN_SERVICE_URL'), json=[])

        Signer(self.document).start_signing()

        self.assertEqual(
            Document.final_state,
            api.content.get_state(self.document)
        )

    def test_update_signing_state(self, mocker):
        self.login(self.regular_user)

        # prepare signing
        mocker.post(environ.get('SIGN_SERVICE_URL'), json=[])
        token = Signer(self.document).start_signing()

        Signer(self.document).update_signing_state(token, 'failed')

        self.assertEqual(
            'failed',
            Signer(self.document).storage.get(token)['state'])

    def test_add_signed_version_creates_new_version_with_the_signed_file(self, mocker):
        self.login(self.regular_user)

        # prepare signing
        mocker.post(environ.get('SIGN_SERVICE_URL'), json=[])
        token = Signer(self.document).start_signing()

        Signer(self.document).add_signed_version(token, u'SIGNED_FILE_DATA')

        # version commment
        version_data = Versioner(self.document).get_version_metadata(1)
        self.assertEqual(u'label_document_signed', version_data['sys_metadata']['comment'])

        # version object
        signed_version = Versioner(self.document).retrieve(1)
        self.assertEqual(u'SIGNED_FILE_DATA', signed_version.file.data)
        self.assertEqual(u'application/pdf', signed_version.file.contentType)
        self.assertEqual(u'Vertraegsentwurf.pdf', signed_version.file.filename)

        # working copy
        self.assertEqual(u'SIGNED_FILE_DATA', self.document.file.data)
        self.assertEqual(u'application/pdf', self.document.file.contentType)
        self.assertEqual(u'Vertraegsentwurf.pdf', self.document.file.filename)
