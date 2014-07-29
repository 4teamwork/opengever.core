from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from ftw.treeview.view import TreeView
import json


class JSONNavigation(TreeView):

    def __call__(self):
        RESPONSE = self.request.RESPONSE
        RESPONSE.setHeader('Content-Type', 'application/json')
        return self.json()

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
