from ftw.bumblebee.interfaces import IBumblebeeServiceV3
from os import environ
from zope.globalrequest import getRequest
import requests


class SignServiceClient(object):

    @property
    def sign_service_url(self):
        return environ.get('SIGN_SERVICE_URL', '').strip('/')

    def queue_signing(self, document, token, signers, editors):
        bumblebee_service = IBumblebeeServiceV3(getRequest())

        return requests.post(
            '{}/signing-jobs/'.format(self.sign_service_url),
            headers={"Accept": "application/json"},
            json={'access_token': token,
                  'document_url': document.absolute_url(),
                  'download_url': bumblebee_service.get_download_url(document),
                  'upload_url': '{}/@upload-signed-pdf'.format(document.absolute_url()),
                  'update_url': '{}/@update-pending-signing-job'.format(document.absolute_url()),
                  'document_uid': document.UID(),
                  'title': document.title_or_id(),
                  'signers': signers,
                  'editors': editors,
                  }).json()

    def abort_signing(self, job_id):
        if job_id is None:
            return

        return requests.delete(
            '{}/signing-jobs/{}'.format(self.sign_service_url, job_id),
            headers={"Accept": "application/json"})


class NullSignServiceClient(object):

    @property
    def sign_service_url(self):
        return environ.get('SIGN_SERVICE_URL', '').strip('/')

    def queue_signing(self, document, token, signers, editors):
        return {}

    def abort_signing(self, job_id):
        pass


sign_service_client = SignServiceClient()
