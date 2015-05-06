from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.inbox.inbox import IInbox
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot


def get_containing_dossier(obj):
    while not IPloneSiteRoot.providedBy(obj):
        if IDossierMarker.providedBy(obj) or IInbox.providedBy(obj):
            return obj
        obj = aq_parent(aq_inner(obj))

    return None
