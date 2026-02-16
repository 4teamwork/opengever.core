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
import os
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
        os.environ['BUMBLEBEE_PUBLIC_URL'] = 'http://bumblebee.local/'

        self.login(self.regular_user)

        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)
        signer = Signer(self.document)

        editors = ['bar.foo@example.com']
        with freeze(FROZEN_NOW):
            signer.start_signing(editors)

        request = mocker.last_request.json()
        request['access_token'] = '<token>'
        request['download_url'] = '<download-url>'
        request['bumblebee_access_token'] = '<bumblebee_access_token>'
        request['bumblebee_convert_url'] = request['bumblebee_convert_url'].split('?')[0]

        self.assertDictEqual(
            {
                u'access_token': u'<token>',
                u'bumblebee_access_token': u'<bumblebee_access_token>',
                u'bumblebee_app_id': u'local',
                u'bumblebee_convert_url': u'http://bumblebee.local/YnVtYmxlYmVl/api/v3/convert',
                u'document_uid': u'createtreatydossiers000000000002',
                u'document_url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14',
                u'download_url': u'<download-url>',
                u'editors': [u'bar.foo@example.com'],
                u'title': u'Vertr\xe4gsentwurf',
                u'upload_url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14/@upload-signed-pdf',
                u'update_url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14/@update-pending-signing-job'
            },
            request
        )

        self.assertDictEqual(
            {
                'created': u'2024-02-18T15:45:00',
                'job_id': '1',
                'redirect_url': 'http://external.example.org/signing-requests/123',
                'invite_url': 'http://external.example.org/invite/signing-requests/123',
                'editors': [{u'email': u'bar.foo@example.com', u'userid': u''}],
                'signatures': [],
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
        signed_versions = signer.signed_versions_storage.load()
        signed_versions.add_signed_version(SignedVersion(version=1))
        signed_versions.add_signed_version(SignedVersion(version=2))
        signer.signed_versions_storage.store(signed_versions)

        self.assertEqual([1, 2], signer.serialize_signed_versions().keys())

    def test_can_update_pending_signing_job(self, mocker):
        self.login(self.regular_user)
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        signer = Signer(self.document)
        signer.start_signing(['foo.bar@example.com'])

        self.assertItemsEqual(
            [{u'userid': u'', u'email': u'foo.bar@example.com'}],
            signer.pending_signing_job.serialize().get('editors'))

        signer.update_pending_signing_job(editors=['updated@example.com'])

        self.assertItemsEqual(
            [{u'userid': u'', u'email': u'updated@example.com'}],
            signer.pending_signing_job.serialize().get('editors'))

    def test_signed_versions_are_dropped_after_copy_obj(self, mocker):
        self.login(self.regular_user)

        signer = Signer(self.document)
        signed_versions = signer.signed_versions_storage.load()
        signed_versions.add_signed_version(SignedVersion(version=1))
        signer.signed_versions_storage.store(signed_versions)

        document_copy = api.content.copy(source=self.document,
                                         target=self.dossier)

        self.assertEqual(1, len(signer.serialize_signed_versions().keys()))
        self.assertEqual(0, len(Signer(document_copy).serialize_signed_versions().keys()))

    def test_pending_signing_job_is_dropped_after_copy_obj(self, mocker):
        self.login(self.regular_user)
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        Signer(self.document).start_signing(['foo.bar@example.com'])

        document_copy = api.content.copy(source=self.document,
                                         target=self.dossier)

        self.assertIsNotNone(Signer(self.document).pending_signing_job)
        self.assertIsNone(Signer(document_copy).pending_signing_job)
