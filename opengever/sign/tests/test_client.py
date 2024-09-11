from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from opengever.sign.client import SignServiceClient
from opengever.testing import IntegrationTestCase
import re
import requests_mock


DEFAULT_MOCK_RESPONSE = {
    'id': '1',
    'redirect_url': 'http://external.example.org/signing-requests/123',
}

TOKEN = '<access-token>'


@requests_mock.Mocker()
class TestSigningClient(IntegrationTestCase):

    def test_add_a_signing_job(self, mocker):
        self.login(self.regular_user)

        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        SignServiceClient().queue_signing(self.document, TOKEN, ['foo.bar@example.com'])

        self.assertDictEqual(
            {
                u'access_token': u'<access-token>',
                u'document_uid': u'createtreatydossiers000000000002',
                u'document_url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14', # noqa
                u'download_url': u'http://nohost/plone/bumblebee_download?checksum={}&uuid=createtreatydossiers000000000002'.format(DOCX_CHECKSUM), # noqa
                u'signers': ['foo.bar@example.com'],
                u'title': u'Vertr\xe4gsentwurf',
                u'upload_url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14/@upload-signed-pdf', # noqa
            },
            mocker.last_request.json())

    def test_abort_signing_job(self, mocker):
        self.login(self.regular_user)

        mocker.delete(re.compile('/signing-jobs/123'))

        response = SignServiceClient().abort_signing('123')

        self.assertEqual(200, response.status_code)
