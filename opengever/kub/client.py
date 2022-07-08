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

    @ram.cache(lambda *args: time() // (60 * 60))
    def get_kub_id_label_mapping(self):
        items = {}
        self._fetch_kub_items(items, url_name='people', kub_type='person')
        self._fetch_kub_items(items, url_name='organizations', kub_type='organization')
        self._fetch_kub_items(items, url_name='memberships', kub_type='membership')
        return items

    def _fetch_kub_items(self, mapping, url=None, url_name=None, kub_type=None):
        if not url:
            # KuB only supports a pageSize of 10000 - for whatever reason
            url = u'{}/{}?page1&pageSize=10000'.format(self.kub_api_url, url_name)

        resp = self.session.get(url)
        data = resp.json()
        for item in data.get('results', []):
            mapping['{}:{}'.format(kub_type, item['id'])] = item['fullName']

        if data.get('next'):
            self._fetch_kub_items(mapping, url=data.get('next'),
                                  url_name=url_name, kub_type=kub_type)

        return mapping
