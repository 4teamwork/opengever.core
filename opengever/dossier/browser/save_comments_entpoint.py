from opengever.dossier.behaviors.dossier import IDossier
from Products.Five.browser import BrowserView
import json


class SaveCommentsEndpoint(BrowserView):

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        self.request.response.setHeader('X-Theme-Disabled', 'True')

        data = json.loads(self.request.get('data', '{}'))
        dossier = IDossier(self.context)
        dossier.comments = data['comments']
        self.context.reindexObject(idxs=['SearchableText'])
        return json.dumps({'comment': self.context.get_formatted_comments()})
