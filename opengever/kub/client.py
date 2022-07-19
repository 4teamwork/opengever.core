from opengever.base.sentry import log_msg_to_sentry
from opengever.kub.interfaces import IKuBSettings
from plone import api
from plone.memoize import ram
from time import time
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
        url = self.get_resolve_url(_id)
        resp = self.session.get(url)
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            log_msg_to_sentry(exc.message)
            raise LookupError
        return resp.json()

    def get_resolve_url(self, _id):
        return u'{}resolve/{}'.format(self.kub_api_url, _id)

    # Cache kub labels for an hour
    @ram.cache(lambda *args: time() // (60 * 60))
    def get_kub_id_label_mapping(self):
        return self._prepare_kub_label_mapping()

    def _prepare_kub_label_mapping(self):
        resp = self.session.get(u'{}labels'.format(self.kub_api_url))
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            log_msg_to_sentry(exc.message)
            raise LookupError
        return {
            item['typedId']: item['label'] for item in resp.json()['results']}
