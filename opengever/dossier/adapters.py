from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.dossier.behaviors.dossier import IDossierMarker
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class IParentDossierFinder(Interface):
    """Adapter interface for finding the parent dossier of a context.
    """

    def find_dossier():
        """Returns the first parent dossier of the adapted context.
        """


@implementer(IParentDossierFinder)
@adapter(Interface)
class ParentDossierFinder(object):

    def __init__(self, context):
        self.context = context

    def find_dossier(self):
        obj = self.context

        while not IPloneSiteRoot.providedBy(obj):
            if IDossierMarker.providedBy(obj):
                return obj
            else:
                obj = aq_parent(aq_inner(obj))

        return None
