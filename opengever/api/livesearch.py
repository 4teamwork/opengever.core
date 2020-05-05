from opengever.base.interfaces import ISearchSettings
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

        if api.portal.get_registry_record(
                'use_solr', interface=ISearchSettings, default=False):
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

        else:
            del self.request.form['q']

            # Strip VHM path because plone.restapi SearchHandler will add it
            vhm_physical_path = '/'.join(
                self.request.get('VirtualRootPhysicalPath', ''))
            if vhm_physical_path:
                if path.startswith(vhm_physical_path):
                    path = path[len(vhm_physical_path):]
                    if not path:
                        path = '/'

            self.request.form.update({
                'SearchableText': search_term + '*',
                'sort_limit': limit,
                'path': path,
                'metadata_fields': ['Title', 'filename', 'id', 'portal_type']
            })

            response = super(GeverLiveSearchGet, self).reply()

            results = []
            for entry in response['items'][:limit]:
                result = {
                    'title': entry['title'],
                    'filename': entry['filename'],
                    '@id': entry['@id'],
                    '@type': entry['@type'],
                    'review_state': entry['review_state'],
                    'is_leafnode': entry['is_leafnode'],
                }
                if is_dossierish_portal_type(entry.get('@type', '')):
                    result['is_subdossier'] = entry['is_subdossier']
                results.append(result)
            return results
