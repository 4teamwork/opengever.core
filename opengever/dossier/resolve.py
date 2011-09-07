#from Acquisition import aq_inner, aq_parent
#from Products.statusmessages.interfaces import IStatusMessage
from five import grok
#from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker
#from opengever.dossier.behaviors.dossier import IDossier


class Resolve(grok.View):

    grok.context(IDossierMarker)
    grok.name('transition-resolve')
    grok.require('zope2.View')

    def render(self):
        return self.context.recursively_resolve()
