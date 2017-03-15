from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.inbox.inbox import IInbox
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
import unicodedata


ELLIPSIS = unicodedata.lookup('HORIZONTAL ELLIPSIS')


def get_containing_dossier(obj):
    while not IPloneSiteRoot.providedBy(obj):
        if IDossierMarker.providedBy(obj) or IInbox.providedBy(obj):
            return obj
        obj = aq_parent(aq_inner(obj))

    return None


def get_main_dossier(obj):
    """Helper method which returns the main dossier (or inbox) of the given
    object.
    If the given object is not storred inside a dossier it returns None."""

    dossier = None
    while not IPloneSiteRoot.providedBy(obj):
        if IDossierMarker.providedBy(obj) or IInbox.providedBy(obj):
            dossier = obj

        obj = aq_parent(aq_inner(obj))

    return dossier


def truncate_ellipsis(text, threshold, ellipsis=" " + ELLIPSIS):
    return (text[:threshold] + ellipsis) if len(text) > threshold else text
