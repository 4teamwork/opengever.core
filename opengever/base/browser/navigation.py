from AccessControl import getSecurityManager
from DateTime import DateTime
from opengever.base.utils import get_preferred_language_code
from opengever.repository.repositoryfolder import REPOSITORY_FOLDER_STATE_INACTIVE
from opengever.sqlcatalog.interfaces import ISQLCatalog
from pkg_resources import get_distribution
from Products.Five import BrowserView
from sqlalchemy.sql.expression import desc
from zope.component import getUtility
import json
import os.path


def make_tree_by_url(nodes):
    """Creates a nested tree of nodes from a flat list-like object of nodes.
    Each node is expected to be a dict with a url-like string stored
    under the key ``url``.
    Each node will end up with a ``nodes`` key, containing a list
    of children nodes.
    The nodes are changed in place, be sure to make copies first when
    necessary.
    """

    for node in nodes:
        node['nodes'] = []

    nodes_by_url = dict((node['url'], node) for node in nodes)
    root = []

    for node in nodes:
        parent_url = os.path.dirname(node['url'])
        if parent_url in nodes_by_url:
            nodes_by_url[parent_url]['nodes'].append(node)
        else:
            root.append(node)

    return root


class JSONNavigation(BrowserView):

    def __call__(self):
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')
        response.enableHTTPCompression(REQUEST=self.request)

        if self.request.get('cache_key'):
            # Only cache when there is a cache_key in the request.
            # Representations may be cached by any cache.
            # The cached representation is to be considered fresh for 1 year
            # http://stackoverflow.com/a/3001556/880628
            response.setHeader('Cache-Control', 'private, max-age=31536000')

        return self.json()

    def get_caching_url(self):
        url = self.context.absolute_url() + '/navigation.json'
        params = []
        cache_key = self._navigation_cache_key()
        if cache_key:
            params.append('cache_key={0}'.format(cache_key))

        if self.request.getHeader('Cache-Control') == 'no-cache':
            params.append('nocache=true')

        params.append('language={}'.format(get_preferred_language_code()))

        if params:
            url = '{0}?{1}'.format(url, '&'.join(params))

        return url

    def json(self):
        return json.dumps(self._tree())

    def query(self):
        query = getUtility(ISQLCatalog).get_model_for_portal_type(
            'opengever.repository.repositoryfolder').query
        query = query.order_by('title')
        return query

    def _tree(self):
        nodes = map(self._brain_to_node, self.query())
        return make_tree_by_url(nodes)

    def _brain_to_node(self, record):
        return {'text': record.title.encode('utf-8'),
                'description': '',
                'url': record.getURL(),
                'uid': record.uuid.encode('utf-8'),
                'active': record.review_state != REPOSITORY_FOLDER_STATE_INACTIVE, }

    def _navigation_cache_key(self):
        last_modified = self._get_newest_modification_timestamp()
        if last_modified is not None:
            version = get_distribution('opengever.core').version
            username = getSecurityManager().getUser().getId()
            return '-'.join((version, last_modified, username))
        else:
            return None

    def _get_newest_modification_timestamp(self):
        query = self.query().order_by(None).order_by(desc('modified'))
        last_modified_record = query.first()
        if last_modified_record is None:
            return None

        return str(DateTime(last_modified_record.modified).millis())
