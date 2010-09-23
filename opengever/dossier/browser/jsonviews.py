from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from five import grok
from opengever.dossier.behaviors.dossier import IDossierMarker
import json


class OpenDossiersAsJSONView(grok.CodeView):
    grok.context(IPloneSiteRoot)
    grok.name('list-open-dossiers-json')

    def render(self):
        data = []
        brains = self.context.portal_catalog(
            object_provides=IDossierMarker.__identifier__,
            review_state='dossier-state-active',
            )

        portal_path = '/'.join(self.context.getPhysicalPath())

        for brain in brains:
            path = brain.getPath()[len(portal_path) + 1:]
            data.append({
                    'path': path,
                    'url': str(brain.getURL()),
                    'title': str(safe_unicode(
                            brain.Title).encode('utf8')),
                    'review_state': str(brain.review_state),
                    'reference_number': str(brain.reference_number),
                    })
        return json.dumps(data)
