from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from opengever.sign.client import SignServiceClient
from opengever.testing import IntegrationTestCase
import os
import re
import requests_mock


DEFAULT_MOCK_RESPONSE = {
    'id': '1',
    'redirect_url': 'http://external.example.org/signing-requests/123',
}

TOKEN = '<access-token>'


@requests_mock.Mocker()
class TestSigningClient(IntegrationTestCase):
    def tearDown(self):
        os.environ['BUMBLEBEE_PUBLIC_URL'] = 'http://bumblebee.local/'
        if 'SIGN_SERVICE_GEVER_URL' in os.environ:
            del os.environ['SIGN_SERVICE_GEVER_URL']

    def test_add_a_signing_job(self, mocker):
        self.login(self.regular_user)

        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        editors = ['foo@example.com']
        response = SignServiceClient().queue_signing(
            self.document, TOKEN, editors)

        request_json = mocker.last_request.json()
        request_json['bumblebee_access_token'] = '<bumblebee_access_token>'
        request_json['bumblebee_convert_url'] = request_json['bumblebee_convert_url'].split('?')[0]

        self.assertDictEqual(
            {
                u'access_token': u'<access-token>',
                u'bumblebee_access_token': u'<bumblebee_access_token>',
                u'bumblebee_app_id': u'local',
                u'bumblebee_convert_url': u'http://bumblebee.local/YnVtYmxlYmVl/api/v3/convert',
                u'document_uid': u'createtreatydossiers000000000002',
                u'document_url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14', # noqa
                u'download_url': u'http://nohost/plone/bumblebee_download?checksum={}&uuid=createtreatydossiers000000000002'.format(DOCX_CHECKSUM), # noqa
                u'editors': ['foo@example.com'],
                u'title': u'Vertr\xe4gsentwurf',
                u'upload_url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14/@upload-signed-pdf', # noqa
                u'update_url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14/@update-pending-signing-job', # noqa
            },
            request_json)

        self.assertDictEqual(DEFAULT_MOCK_RESPONSE, response)

    def test_abort_signing_job(self, mocker):
        self.login(self.regular_user)

        mocker.delete(re.compile('/signing-jobs/123'))

        response = SignServiceClient().abort_signing('123')

        self.assertEqual(200, response.status_code)

    def test_can_use_a_different_gever_callback_url(self, mocker):
        self.login(self.regular_user)
        os.environ['SIGN_SERVICE_GEVER_URL'] = "http://example.com/mygever"

        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        response = SignServiceClient().queue_signing(
            self.document, TOKEN, [])

        request_json = mocker.last_request.json()
        request_json['bumblebee_access_token'] = '<bumblebee_access_token>'
        request_json['bumblebee_convert_url'] = request_json['bumblebee_convert_url'].split('?')[0]

        self.assertDictEqual(
            {
                u'access_token': u'<access-token>',
                u'bumblebee_access_token': u'<bumblebee_access_token>',
                u'bumblebee_app_id': u'local',
                u'bumblebee_convert_url': u'http://bumblebee.local/YnVtYmxlYmVl/api/v3/convert',
                u'document_uid': u'createtreatydossiers000000000002',
                u'document_url': u'http://example.com/mygever/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14', # noqa
                u'download_url': u'http://nohost/plone/bumblebee_download?checksum={}&uuid=createtreatydossiers000000000002'.format(DOCX_CHECKSUM), # noqa
                u'editors': [],
                u'title': u'Vertr\xe4gsentwurf',
                u'upload_url': u'http://example.com/mygever/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14/@upload-signed-pdf', # noqa
                u'update_url': u'http://example.com/mygever/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14/@update-pending-signing-job', # noqa
            },
            request_json)

        self.assertDictEqual(DEFAULT_MOCK_RESPONSE, response)
