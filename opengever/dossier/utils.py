from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.inbox.inbox import IInbox
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
import unicodedata


ELLIPSIS = unicodedata.lookup('HORIZONTAL ELLIPSIS')


def get_containing_dossier(obj):
    while obj and not IPloneSiteRoot.providedBy(obj):
        if IDossierMarker.providedBy(obj) or IInbox.providedBy(obj):
            return obj
        obj = aq_parent(aq_inner(obj))
    return None


def find_parent_dossier(content):
    """Returns the first parent dossier (or inbox) relative to the current context.
    """

    if IPloneSiteRoot.providedBy(content):
        raise ValueError('Site root passed as argument.')

    while content and not (IDossierMarker.providedBy(content) or IInbox.providedBy(content)):
        content = aq_parent(aq_inner(content))
        if IPloneSiteRoot.providedBy(content):
            raise ValueError('Site root reached while searching '
                             'parent dossier.')
    return content


def get_main_dossier(obj):
    """Helper method which returns the main dossier (or inbox) of the given
    object.
    If the given object is not storred inside a dossier it returns None."""

    dossier = None
    while obj and not IPloneSiteRoot.providedBy(obj):
        if IDossierMarker.providedBy(obj) or IInbox.providedBy(obj):
            dossier = obj

        obj = aq_parent(aq_inner(obj))

    return dossier


def truncate_ellipsis(text, threshold, ellipsis=ELLIPSIS):
    if text:
        text = safe_unicode(text)
        return (text[:threshold] + ellipsis) if len(text) > threshold else text
    else:
        return ''
