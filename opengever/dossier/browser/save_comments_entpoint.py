from opengever.dossier.behaviors.dossier import IDossier
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides
import json


class SaveCommentsEndpoint(BrowserView):

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        self.request.response.setStatus(204)

        data = json.loads(self.request.get('data', '{}'))
        dossier = IDossier(self.context)
        dossier.comments = data['comments']
        self.context.reindexObject(idxs=['SearchableText'])
        return None
