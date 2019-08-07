from opengever.repository.interfaces import IDuringRepositoryDeletion
from plone import api
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zExceptions import Forbidden
from zope.container.interfaces import IContainerModifiedEvent


def is_reference_number_prefix_changed(descriptions):
    for desc in descriptions:
        for attr in desc.attributes:
            if attr == 'IReferenceNumberPrefix.reference_number_prefix':
                return True
    return False


def update_reference_prefixes(obj, event):
    """A eventhandler which reindex all contained objects, if the
    reference prefix has been changed.
    """
    if ILocalrolesModifiedEvent.providedBy(event) or \
       IContainerModifiedEvent.providedBy(event):
        return

    if is_reference_number_prefix_changed(event.descriptions):
        catalog = api.portal.get_tool('portal_catalog')
        children = catalog.unrestrictedSearchResults(
            path='/'.join(obj.getPhysicalPath()))
        for child in children:
            child.getObject().reindexObject(idxs=['reference'])


def check_delete_preconditions(repository, event):
    """It's not allowed to delete repository folders or the repository root
    """

    # Ignore plone site deletions
    if IPloneSiteRoot.providedBy(event.object):
        return

    # Allow deletion done through the RepositoryDeleter
    if IDuringRepositoryDeletion.providedBy(event.object.REQUEST):
        return

    raise Forbidden('Deleting repository folders and roots is not allowed')
