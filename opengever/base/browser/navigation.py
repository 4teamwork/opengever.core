from AccessControl import getSecurityManager
from opengever.base.utils import get_preferred_language_code
from opengever.repository.repositoryfolder import REPOSITORY_FOLDER_STATE_INACTIVE
from pkg_resources import get_distribution
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
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
        interfaces = (
            'opengever.repository.repositoryfolder.IRepositoryFolderSchema',
        )
        return {'object_provides': interfaces,
                'path': '/'.join(self.context.getPhysicalPath()),
                'sort_on': 'sortable_title'}

    def _tree(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(self.query())
        nodes = map(self._brain_to_node, brains)
        return make_tree_by_url(nodes)

    def _brain_to_node(self, brain):
        return {'text': brain.Title,
                'description': brain.Description,
                'url': brain.getURL(),
                'uid': brain.UID,
                'active': brain.review_state != REPOSITORY_FOLDER_STATE_INACTIVE, }

    def _navigation_cache_key(self):
        last_modified = self._get_newest_modification_timestamp()
        if last_modified is not None:
            version = get_distribution('opengever.core').version
            username = getSecurityManager().getUser().getId()
            return '-'.join((version, last_modified, username))
        else:
            return None

    def _get_newest_modification_timestamp(self):
        """Returns the timestamp (in milliseconds) of the latest modification
        that happened to any object in the navigation.

        The problem here is that the ``modified`` index's precision is minutes.
        This means that when multiple objects are modified in the same minute,
        the order of a modified-ordered query may be wrong.

        We therefore must make sure that we consider enough brains in order to
        be sure that the timestamp is really accurate.

        This was previously implemented with a separate modified_seconds index,
        which turned out to be a bad idea (conflict errors, performance).
        """

        query = self.query()
        # Also include repository root:
        query['object_provides'] += (
            'opengever.repository.repositoryroot.IRepositoryRoot',
        )
        query['sort_on'] = 'modified'
        query['sort_order'] = 'reverse'
        query['sort_limit'] = 100

        brains = getToolByName(self.context, 'portal_catalog')(query)
        if len(brains) == 0:
            return None

        # Walk through the brains as long as the brain's modification
        # timestamp is in the same minute; that is the set of brains
        # which the modified-index of the catalog cannot order correctly.
        # When we reach the next minute, return the newest modification
        # timestamp.
        minute_of = lambda stamp: stamp.strftime('%Y-%m-%d %H:%M')
        previous = None
        newest = None
        for brain in brains:
            newest = max(brain.modified, newest)
            if previous and minute_of(previous) != minute_of(brain.modified):
                break
            previous = brain.modified

        return str(newest.millis())
