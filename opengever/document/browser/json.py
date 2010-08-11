from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from five import grok
from opengever.document.document import IDocumentSchema
import simplejson


class DocumentsOfDossierAsJSONView(grok.CodeView):
    """This view provides a json representation of all visible documents
    of a dossier (REQUEST['dossier']) on this client.

    """
    grok.context(IPloneSiteRoot)
    grok.name('tentacle-documents-of-dossier-json')

    def render(self):
        # absolute path to dossier on this client:
        dossier = self.request.get('dossier')
        data = []
        brains = self.context.portal_catalog(
            path=str(dossier),
            object_provides=IDocumentSchema.__identifier__,
            )
        for brain in brains:
            data.append({
                    'path': str(brain.getPath()),
                    'url': str(brain.getURL()),
                    'title': str(safe_unicode(brain.Title).encode('utf8')),
                    'review_state': str(brain.review_state),
                    })
        return simplejson.dumps(data)
