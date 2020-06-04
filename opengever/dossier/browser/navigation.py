from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_filters
from opengever.base.browser.navigation import make_tree_by_url
from opengever.base.solr import OGSolrContentListing
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from plone import api
from Products.Five import BrowserView
from zope.component import getUtility
import json


class DossierJSONNavigation(BrowserView):
    """Return a JSON-navigation structure for a dossier (context) and its
    subdossiers.

    The navigation starts at the current context, i.e. the dossier.

    """

    filters = {
        'object_provides': IDossierMarker.__identifier__,
        'review_state': DOSSIER_STATES_OPEN,
    }

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
        solr = getUtility(ISolrSearch)
        filters = make_filters(
            trashed=False,
            path={
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': -1,
            },
            **self.filters
        )
        fieldlist = ['UID', 'Title', 'Description', 'path']
        resp = solr.search(
            filters=filters, start=0, rows=100000, sort='sortable_title asc',
            fl=fieldlist)

        def contentlisting_object_to_node(obj):
            return {
                'text': obj.Title(),
                'description': obj.Description(),
                'url': obj.getURL(),
                'uid': obj.UID,
            }

        if resp.num_found > 1:
            nodes = map(
                contentlisting_object_to_node, OGSolrContentListing(resp))
        else:
            nodes = []

        return make_tree_by_url(nodes)


class DossierTemplateJSONNavigation(DossierJSONNavigation):
    filters = {
        'object_provides': IDossierTemplateMarker.__identifier__,
    }
