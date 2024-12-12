from base64 import b64encode
from datetime import datetime
from ftw.testing import freeze
from opengever.document.document import Document
from opengever.document.versioner import Versioner
from opengever.sign.sign import Signer
from opengever.sign.signed_version import SignedVersion
from opengever.sign.token import InvalidToken
from opengever.testing import IntegrationTestCase
from plone import api
import re
import requests_mock


FROZEN_NOW = datetime(2024, 2, 18, 15, 45)

DEFAULT_MOCK_RESPONSE = {
    'id': '1',
    'redirect_url': 'http://external.example.org/signing-requests/123',
    'invite_url': 'http://external.example.org/invite/signing-requests/123',
}


@requests_mock.Mocker()
class TestSigning(IntegrationTestCase):

    features = ['sign']

    def test_store_signing_document_metadata_when_starting_sign_process(self, mocker):
        self.login(self.regular_user)

        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)
        signer = Signer(self.document)

        signers = ['foo.bar@example.com']
        editors = ['bar.foo@example.com']
        with freeze(FROZEN_NOW):
            signer.start_signing(signers, editors)

        request = mocker.last_request.json()
        request['access_token'] = '<token>'
        request['download_url'] = '<download-url>'

        self.assertDictEqual(
            {
                u'access_token': u'<token>',
                u'document_uid': u'createtreatydossiers000000000002',
                u'document_url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14',
                u'download_url': u'<download-url>',
                u'editors': [u'bar.foo@example.com'],
                u'signers': [u'foo.bar@example.com'],
                u'title': u'Vertr\xe4gsentwurf',
                u'upload_url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14/@upload-signed-pdf'
            },
            request
        )

        self.assertDictEqual(
            {
                'created': u'2024-02-18T15:45:00',
                'job_id': '1',
                'redirect_url': 'http://external.example.org/signing-requests/123',
                'invite_url': 'http://external.example.org/invite/signing-requests/123',
                'signers': [{u'email': u'foo.bar@example.com', u'userid': u''}],
                'editors': [{u'email': u'bar.foo@example.com', u'userid': u''}],
                'userid': 'regular_user',
                'version': 0
            }, signer.serialize_pending_signing_job())

    def test_can_issue_and_invalidate_tokens(self, mocker):
        self.login(self.regular_user)

        signer = Signer(self.document)
        token = signer.issue_token()
        self.assertTrue(signer.validate_token(token))

        signer.invalidate_token()
        with self.assertRaises(InvalidToken):
            signer.validate_token(token)

    def test_can_abort_signing_process(self, mocker):
        self.login(self.regular_user)
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)
        delete_mocker = mocker.delete(re.compile('/signing-jobs/1'))

        signer = Signer(self.document)
        token = signer.start_signing(['foo.bar@example.com'])
        signer.abort_signing()

        # current token should be invalidated
        with self.assertRaises(InvalidToken):
            signer.validate_token(token)

        # signing-job should be removed
        self.assertEqual(1, delete_mocker.call_count)

        # pending signing job should be cleared
        self.assertEqual({}, signer.serialize_pending_signing_job())

    def test_can_complete_signing_process(self, mocker):
        self.login(self.regular_user)
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)
        api.content.transition(obj=self.document,
                               transition=Document.draft_signing_transition)

        signer = Signer(self.document)

        self.assertEqual(0, self.document.get_current_version_id(missing_as_zero=True))
        self.assertEqual(0, len(signer.signed_versions_storage.load().values()))

        signer.complete_signing(b64encode('<DATA>'))

        self.assertEqual(1, self.document.get_current_version_id(missing_as_zero=True))

        signed_version = Versioner(self.document).retrieve(1)
        self.assertEqual(u'<DATA>', signed_version.file.data)

        # pending signing job should be cleared
        self.assertEqual({}, signer.serialize_pending_signing_job())

        # a new signature item should have been created
        self.assertEqual(1, len(signer.signed_versions_storage.load().values()))
        self.assertEqual(1, signer.signed_versions_storage.load().values()[0].version)

    def test_can_serialize_signed_versions(self, mocker):
        self.login(self.regular_user)

        signer = Signer(self.document)
        storage = signer.signed_versions_storage.load()
        storage.add_signed_version(SignedVersion(version=1))
        storage.add_signed_version(SignedVersion(version=2))

        self.assertEqual([1, 2], signer.serialize_signed_versions().keys())
