from opengever.base.browser.navigation import make_tree_by_url
from opengever.dossier.base import DOSSIER_STATES_OPEN
from plone import api
from Products.Five import BrowserView
import json


class JSONNavigation(BrowserView):
    """Return a JSON-navigation structure for a dossier (context) and its
    subdossiers.

    The navigation starts at the current context, i.e. the dossier.

    """

    def __call__(self):
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')

        return self.json()

    def json(self):
        return json.dumps(self._tree())

    def _context_as_node(self):
        return {'text': self.context.title,
                'description': self.context.description,
                'url': self.context.absolute_url(),
                'uid': api.content.get_uuid(obj=self.context)}

    def _tree(self):
        nodes = map(
            self._brain_to_node,
            self.context.get_subdossiers(sort_on='sortable_title',
                                         review_state=DOSSIER_STATES_OPEN))
        if nodes:
            nodes = [self._context_as_node()] + nodes
        return make_tree_by_url(nodes)

    def _brain_to_node(self, brain):
        return {'text': brain.Title,
                'description': brain.Description,
                'url': brain.getURL(),
                'uid': brain.UID}
