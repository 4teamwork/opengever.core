from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from five import grok
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossierMarker
import json


class OpenDossiersAsJSONView(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('list-open-dossiers-json')
    grok.require('zope2.View')

    def render(self):
        data = []
        brains = self.context.portal_catalog(
            object_provides=IDossierMarker.__identifier__,
            review_state=DOSSIER_STATES_OPEN,
            )

        portal_path = '/'.join(self.context.getPhysicalPath())

        for brain in brains:
            path = brain.getPath()[len(portal_path) + 1:]
            data.append({
                'path': path,
                'url': str(brain.getURL()),
                'title': str(safe_unicode(brain.Title).encode('utf8')),
                'review_state': str(brain.review_state),
                'reference_number': str(brain.reference),
                })

        # Set correct content type for JSON response
        self.request.response.setHeader("Content-type", "application/json")

        return json.dumps(data)
