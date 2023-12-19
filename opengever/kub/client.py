from datetime import datetime
from opengever.base.sentry import log_msg_to_sentry
from opengever.kub.interfaces import IKuBSettings
from persistent.mapping import PersistentMapping
from plone import api
from plone.memoize import ram
from time import mktime
from time import time
from urllib import urlencode
from wsgiref.handlers import format_date_time
from zope.annotation import IAnnotations
import requests


KUB_API_VERSION = 'v2'


class KuBClient(object):

    STORAGE_MODIFIED_KEY = 'opengever.kub.storage.modified'
    STORAGE_LABEL_MAPPING_KEY = 'opengever.kub.storage.label_mapping'

    def __init__(self):
        self._storage = IAnnotations(api.portal.get())
        if self.STORAGE_MODIFIED_KEY not in self._storage:
            self._storage[self.STORAGE_MODIFIED_KEY] = None
        if self.STORAGE_LABEL_MAPPING_KEY not in self._storage:
            self._storage[self.STORAGE_LABEL_MAPPING_KEY] = None

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
        language_tool = api.portal.get_tool('portal_languages')
        language = language_tool.getPreferredLanguage()
        session.headers.update(
            {'Accept-Language': language,
             'Authorization': 'Token {}'.format(self.kub_service_token)})
        return session

    def query(self, query_str, filters=dict()):
        search_filters = {
            'q': query_str,
        }
        search_filters.update(filters)
        url = u'{}search?{}'.format(self.kub_api_url, urlencode(search_filters))
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

    # Cache kub labels for 5 seconds
    @ram.cache(lambda *args: time() // (5))
    def get_kub_id_label_mapping(self):
        self._update_kub_label_mapping()
        return self._storage[self.STORAGE_LABEL_MAPPING_KEY]

    def _update_kub_label_mapping(self):
        now = datetime.now()
        modified = self._storage[self.STORAGE_MODIFIED_KEY]
        headers = {'If-Modified-Since': modified} if modified else {}
        resp = self.session.get(u'{}labels'.format(self.kub_api_url), headers=headers)
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            log_msg_to_sentry(exc.message)
            raise LookupError

        if resp.status_code == 200:
            self._storage[self.STORAGE_LABEL_MAPPING_KEY] = PersistentMapping(
                {item['typedId']: item['label'] for item in resp.json()['results']})
            stamp = mktime(now.timetuple())
            self._storage[self.STORAGE_MODIFIED_KEY] = format_date_time(stamp)
