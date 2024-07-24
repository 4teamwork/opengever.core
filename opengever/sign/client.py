from os import environ
import requests


class SignServiceClient(object):

    @property
    def sign_service_url(self):
        return environ.get('SIGN_SERVICE_URL')

    def queue_signing(self, document, token):
        resp = requests.post(
            self.sign_service_url,
            data={'token': token,
                  'url': document.absolute_url(),
                  'file': document.get_file().data})
