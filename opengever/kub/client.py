from opengever.kub.interfaces import IKuBSettings
from plone import api
import requests


KUB_API_VERSION = 'v1'


class KuBClient(object):

    @property
    def request(self):
        """Returns the request object from the current session.
        """
        return self.session.request

    @property
    def kub_api_url(self):
        return u'{}/api/{}/'.format(
            api.portal.get_registry_record(name='base_url', interface=IKuBSettings),
            KUB_API_VERSION)

    @property
    def kub_service_token(self):
        return api.portal.get_registry_record(
            name='service_token', interface=IKuBSettings)

    @property
    def session(self):
        session = requests.Session()
        session.headers.update(
            {'Authorization': 'Token {}'.format(self.kub_service_token)})

        return session

    def query(self, query_str):
        url = u'{}search?q={}'.format(self.kub_api_url, query_str)
        res = self.session.get(url)
        return res.json()

    def get_by_id(self, _id):
        url = u'{}search?id={}'.format(self.kub_api_url, _id)
        res = self.session.get(url).json()
        if len(res) != 1:
            raise LookupError()
        return res[0]
