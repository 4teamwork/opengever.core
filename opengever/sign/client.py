from ftw.bumblebee.config import bumblebee_config
from ftw.bumblebee.hashing import get_conversion_access_token
from ftw.bumblebee.interfaces import IBumblebeeServiceV3
from os import environ
from plone import api
from zope.globalrequest import getRequest
import os
import requests


class SignServiceClient(object):

    @property
    def sign_service_url(self):
        return environ.get('SIGN_SERVICE_URL', '').strip('/')

    @property
    def sign_service_gever_url(self):
        """An URL which point to gever and is accessible by the sign service.
        """
        sign_gever_url = environ.get('SIGN_SERVICE_GEVER_URL', '').strip('/')
        return sign_gever_url or api.portal.get().absolute_url()

    def construct_callback_url(self, url):
        return url.replace(api.portal.get().absolute_url(),
                           self.sign_service_gever_url)

    def queue_signing(self, document, token, editors):
        bumblebee_service = IBumblebeeServiceV3(getRequest())
        document_url = self.construct_callback_url(document.absolute_url())

        resp = requests.post(
            '{}/signing-jobs/'.format(self.sign_service_url),
            headers={"Accept": "application/json"},
            json={'access_token': token,
                  'document_url': document_url,
                  'download_url': bumblebee_service.get_download_url(document),
                  'upload_url': '{}/@upload-signed-pdf'.format(document_url),
                  'update_url': '{}/@update-pending-signing-job'.format(document_url),
                  'document_uid': document.UID(),
                  'title': document.title_or_id(),
                  'editors': editors,
                  'bumblebee_convert_url': bumblebee_service.get_convert_url(),
                  'bumblebee_app_id': bumblebee_config.app_id,
                  'bumblebee_access_token': get_conversion_access_token(),
                  })

        resp.raise_for_status()
        return resp.json()

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

    def queue_signing(self, document, token, editors):
        return {}

    def abort_signing(self, job_id):
        pass


client_registry = {
    'ogsign_service': SignServiceClient,
    'null_service': NullSignServiceClient
}


def get_sign_service_client():
    client_name = os.environ.get('SIGN_SERVICE_CLIENT', 'ogsign_service').strip().lower()
    return client_registry[client_name]()
