from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from five import grok
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.octopus.tentacle import utils
import simplejson


class OpenDossiersAsJSONView(grok.CodeView):
    grok.context(IPloneSiteRoot)
    grok.name('tentacle-open-dossiers-json')

    def render(self):
        data = []
        brains = self.context.portal_catalog(
            object_provides=IDossierMarker.__identifier__,
            review_state='dossier-state-active',
            )
        for brain in brains:
            data.append({
                    'path': str(brain.getPath()),
                    'url': str(brain.getURL()),
                    'title': str(utils.aggressive_decode(brain.Title).
                                 encode('utf8')),
                    'review_state': str(brain.review_state),
                    'reference_number': str(brain.reference_number),
                    })
        return simplejson.dumps(data)
