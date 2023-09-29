from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.inbox.inbox import IInbox
from opengever.workspace.interfaces import IWorkspace
from plone import api
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
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
    """Helper method which returns the main dossier/workspace (or inbox) of
    the given object.
    If the given object is not storred inside any main content it returns None."""

    dossier = None
    while obj and not IPloneSiteRoot.providedBy(obj):
        if IDossierMarker.providedBy(obj) or \
           IInbox.providedBy(obj) or \
           IWorkspace.providedBy(obj) or \
           IDossierTemplateSchema.providedBy(obj):
            dossier = obj

        obj = aq_parent(aq_inner(obj))

    return dossier


def is_dossierish_portal_type(portal_type_name):
    """
    Returns a boolean indicating if the given name of the portal type
    is considered a dossier.

    Examples:
    - opengever.dossier.businesscasedossier: True
    - opengever.dossier.dossiertemplate: True
    - opengever.dossier.templatefolder: False

    This is a bit hackish but it's necessary when working with catalog brains
    and Solr results.
    """
    segments = portal_type_name.split('.')
    if segments[0] != 'opengever':
        return False
    return 'dossier' in segments[-1]


def supports_is_subdossier(obj):
    """
    Returns a boolean indicating whether the given object supports
    the is_subdossier index / method.
    """
    return IDossierMarker.providedBy(obj) or IDossierTemplateMarker.providedBy(obj)


def check_subdossier_depth_allowed(subdossier_depth=1):
    """Checks if the maximum dossier depth will be exceeded for a specific
    target depth.
    """
    max_subdossier_depth = api.portal.get_registry_record(
        name='maximum_dossier_depth',
        interface=IDossierContainerTypes,
        default=100,
    )

    return subdossier_depth <= max_subdossier_depth
