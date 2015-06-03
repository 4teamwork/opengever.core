from opengever.base.browser.navigation import make_tree_by_url
from Products.Five import BrowserView
import json
from plone import api


class JSONNavigation(BrowserView):
    """Return a JSON-navigation structure for a dossier (context) and its
    subdossiers.

    The navigation starts at the current context, i.e. the dossier.

    """
    def __call__(self):
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')
        response.enableHTTPCompression(REQUEST=self.request)

        return self.json()

    def json(self):
        return json.dumps(self._tree())

    def _context_as_node(self):
        return {'text': self.context.title,
                'description': self.context.description,
                'url': self.context.absolute_url(),
                'uid': api.content.get_uuid(obj=self.context)}

    def _tree(self):
        subdossier_nodes = map(self._brain_to_node,
                               self.context.get_subdossiers())
        nodes = [self._context_as_node()] + subdossier_nodes

        return make_tree_by_url(nodes)

    def _brain_to_node(self, brain):
        return {'text': brain.Title,
                'description': brain.Description,
                'url': brain.getURL(),
                'uid': brain.UID}
