from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from ftw.treeview.view import TreeView
import json


class JSONNavigation(TreeView):

    def __call__(self):
        RESPONSE = self.request.RESPONSE
        RESPONSE.setHeader('Content-Type', 'application/json')

        if self.request.get('cache_key'):
            # Only cache when there is a cache_key in the request.
            # Representations may be cached by any cache.
            # The cached representation is to be considered fresh for 1 year
            # http://stackoverflow.com/a/3001556/880628
            RESPONSE.setHeader('Cache-Control', 'private, max-age=31536000')
        return self.json()

    def get_caching_url(self):
        url = self.context.absolute_url() + '/navigation.json'
        cache_key = self._navigation_cache_key()
        if cache_key:
            url = '{0}?cache_key={1}'.format(url, cache_key)
        return url

    def json(self):
        current = context = aq_inner(self.context)
        root_path = self.request.get('root_path')
        if root_path:
            portal_url = getToolByName(self.context, 'portal_url')
            current = portal_url.getPortalObject().restrictedTraverse(
                root_path.encode('utf-8'))
        return json.dumps(self.get_tree(context, current))

    def recurse(self, children, **options):
        return map(self.render_node, children)

    def render_node(self, node):
        return {'text': node['Title'],
                'path': node['path'],
                'uid': node['item'].UID,
                'nodes': map(self.render_node, node['children'])}

    def _navigation_cache_key(self):
        cache_relevant = (
            'opengever.repository.repositoryroot.IRepositoryRoot',
            'opengever.repository.repositoryfolder.IRepositoryFolderSchema',
            )

        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog({'object_provides': cache_relevant,
                          'path': '/'.join(self.context.getPhysicalPath()),
                          'sort_on': 'modified',
                          'sort_order': 'reverse',
                          'sort_limit': 1})
        if len(brains):
            return str(brains[0].modified.millis())
        else:
            return None
