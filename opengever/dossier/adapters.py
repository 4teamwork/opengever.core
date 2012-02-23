from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from five import grok
from opengever.dossier.behaviors.dossier import IDossierMarker
from zope.interface import Interface


class IParentDossierFinder(Interface):
    """Adapter interface for finding the parent dossier of a context.
    """

    def find_dossier():
        """Returns the first parent dossier of the adapted context.
        """


class ParentDossierFinder(grok.Adapter):
    grok.context(Interface)
    grok.provides(IParentDossierFinder)
    grok.name('parent-dossier-finder')

    def find_dossier(self):
        obj = self.context

        while not IPloneSiteRoot.providedBy(obj):
            if IDossierMarker.providedBy(obj):
                return obj
            else:
                obj = aq_parent(aq_inner(obj))

        return None
