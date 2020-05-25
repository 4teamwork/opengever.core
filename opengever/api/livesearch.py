from opengever.base.solr import OGSolrContentListing
from opengever.dossier.utils import is_dossierish_portal_type
from plone import api
from plone.restapi.services.search.get import SearchGet
from zope.component import getMultiAdapter


class GeverLiveSearchGet(SearchGet):

    def reply(self):
        search_term = self.request.form.get('q', None)
        limit = int(self.request.form.get('limit', 10))
        portal_path = '/'.join(api.portal.get().getPhysicalPath())
        path = '{}/{}'.format(
            portal_path,
            self.request.form.get('path', '/').lstrip('/'),
        ).rstrip('/')

        if not search_term:
            return []

        view = getMultiAdapter((self.context, self.request),
                               name=u'livesearch_reply')
        view.search_term = search_term
        view.limit = limit
        view.path = path

        results = []
        for entry in OGSolrContentListing(view.results()):
            result = {
                'title': entry.Title(),
                'filename': entry.filename,
                '@id': entry.getURL(),
                '@type': entry.portal_type,
                'review_state': entry.review_state(),
                'is_leafnode': entry.is_leafnode,
            }
            if is_dossierish_portal_type(entry.portal_type):
                result['is_subdossier'] = entry.is_subdossier
            results.append(result)
        return results
