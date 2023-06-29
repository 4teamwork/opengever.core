from opengever.base.security import elevated_privileges
from opengever.document.behaviors import IBaseDocument
from opengever.repository.interfaces import IDuringRepositoryDeletion
from opengever.repository.interfaces import IRepositoryFolder
from plone import api
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zExceptions import Forbidden
from zope.container.interfaces import IContainerModifiedEvent


def reindex_blocked_local_roles(repofolder, event):
    """Reindex blocked_local_roles upon the acquisition blockedness changing."""
    repofolder.reindexObject(idxs=['blocked_local_roles'])


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
        with elevated_privileges():
            for child in children:
                obj = child.getObject()
                idxs = ['reference', 'sortable_reference']
                if IBaseDocument.providedBy(obj):
                    idxs.append('metadata')
                else:
                    idxs.append('SearchableText')

                if IRepositoryFolder.providedBy(obj):
                    idxs += ['Title',
                             'sortable_title',
                             'title_de',
                             'title_fr',
                             'title_en']

                obj.reindexObject(idxs=idxs)


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
