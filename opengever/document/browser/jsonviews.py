from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from five import grok
from opengever.document.document import IDocumentSchema
import json
import os.path


class DocumentsOfDossierAsJSONView(grok.View):
    """This view provides a json representation of all visible documents
    of a dossier (REQUEST['dossier']) on this client.

    """
    grok.context(IPloneSiteRoot)
    grok.name('tentacle-documents-of-dossier-json')
    grok.require('zope2.View')

    def render(self):
        site_path = '/'.join(self.context.getPhysicalPath())
        dossier = os.path.join(site_path, self.request.get('dossier'))
        data = []
        brains = self.context.portal_catalog(
            path=str(dossier),
            object_provides=IDocumentSchema.__identifier__,
            )
        for brain in brains:
            data.append({
                    'path': str(brain.getPath())[len(site_path) + 1:],
                    'url': str(brain.getURL()),
                    'title': str(safe_unicode(brain.Title).encode('utf8')),
                    'review_state': str(brain.review_state),
                    })

        # Set correct content type for JSON response
        self.request.response.setHeader("Content-type", "application/json")

        return json.dumps(data)
