from AccessControl import getSecurityManager
from pkg_resources import get_distribution
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
import json
import os.path


def make_tree_by_path(nodes):
    """Creates a nested tree of nodes from a flat list-like object of nodes.
    Each node is expected to be a dict with a path-like string stored
    under the key ``path``.
    Each node will end up with a ``nodes`` key, containing a list
    of children nodes.
    The nodes are changed in place, be sure to make copies first when
    necessary.
    """

    for node in nodes:
        node['nodes'] = []

    nodes_by_path = dict((node['path'], node) for node in nodes)
    root = []

    for node in nodes:
        parent_path = os.path.dirname(node['path'])
        if parent_path in nodes_by_path:
            nodes_by_path[parent_path]['nodes'].append(node)
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
        return make_tree_by_path(nodes)

    def _brain_to_node(self, brain):
        return {'text': brain.Title,
                'description': brain.Description,
                'path': brain.getPath(),
                'uid': brain.UID}

    def _navigation_cache_key(self):
        query = self.query()
        query['object_provides'] += (
            'opengever.repository.repositoryroot.IRepositoryRoot',
            )
        query['sort_on'] = 'modified_seconds'
        query['sort_order'] = 'reverse'
        query['sort_limit'] = 1

        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(query)
        if len(brains) > 0:
            last_modified = str(brains[0].modified.millis())
            version = get_distribution('opengever.core').version
            username = getSecurityManager().getUser().getId()
            return '-'.join((version, last_modified, username))
        else:
            return None
