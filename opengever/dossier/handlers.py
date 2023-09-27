from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_path_filter
from opengever.api.not_reported_exceptions import Forbidden as NotReportedForbidden
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.base.security import elevated_privileges
from opengever.base.solr import batched_solr_results
from opengever.base.solr import OGSolrDocument
from opengever.bundle.sections.constructor import IDontIssueDossierReferenceNumber
from opengever.dossier import _
from opengever.dossier import is_grant_role_manager_to_responsible_enabled
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.indexers import TYPES_WITH_CONTAINING_SUBDOSSIER_INDEX
from opengever.globalindex.handlers.task import sync_task
from opengever.workspaceclient.interfaces import ILinkedToWorkspace
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from plone import api
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from zope.component import getAdapter
from zope.component import queryUtility
from zope.container.interfaces import IContainerModifiedEvent
from zope.lifecycleevent import IObjectRemovedEvent


def initalize_new_reference_number(obj, event):
    """Initialize new reference_number, to make sure reference number is
    already up to date when child reindex the reference number.
    """

    # Skip if obj is not really moved
    if not event.oldParent or not event.newParent:
        return

    # Skip events for children of the moved container
    if aq_parent(aq_inner(obj)) != event.oldParent:
        return

    # Generate and set the number in the new location
    prefix_adapter = IReferenceNumberPrefix(event.newParent)
    prefix_adapter.set_number(obj)


def set_former_reference_before_moving(obj, event):
    """Temporarily store current reference number before
    moving the dossier.
    """
    # make sure obj wasn't just created or deleted
    if not event.oldParent or not event.newParent:
        return

    dossier_repr = IDossier(obj)
    ref_no = getAdapter(obj, IReferenceNumber).get_number()
    IDossier['temporary_former_reference_number'].set(dossier_repr, ref_no)


def set_former_reference_after_moving(obj, event):
    """Use the (hopefully) stored former reference number
    as the real new former reference number. This has to
    be done after the dossier was moved.

    """
    # make sure obj wasn't just created or deleted
    if not event.oldParent or not event.newParent:
        return

    dossier_repr = IDossier(obj)
    former_ref_no = dossier_repr.temporary_former_reference_number
    IDossier['former_reference_number'].set(dossier_repr, unicode(former_ref_no))
    # reset temporary former reference number
    IDossier['temporary_former_reference_number'].set(dossier_repr, u'')


# Update reference number when adding / moving content
# (IObjectAddedEvent inherits from IObjectMovedEvent)
def save_reference_number_prefix(obj, event):
    if IDontIssueDossierReferenceNumber.providedBy(obj.REQUEST):
        return

    if IObjectRemovedEvent.providedBy(event):
        return

    parent = aq_parent(aq_inner(obj))
    prefix_adapter = IReferenceNumberPrefix(parent)
    if not prefix_adapter.get_number(obj):
        prefix_adapter.set_number(obj)

    obj.reindexObject(idxs=['reference', 'sortable_reference', 'SearchableText'])


def reindex_containing_subdossier_for_contained_objects(dossier, event):
    """When a subdossier is modified, we update the ``containing_subdossier``
    index of all contained objects (documents, mails and tasks) so they don't
    show an outdated title in the ``subdossier`` column
    """
    containing_subdossier_title = dossier.Title()

    solr = queryUtility(ISolrSearch)
    filters = make_path_filter('/'.join(dossier.getPhysicalPath()), depth=-1)
    filters += [
        u'portal_type:({})'.format(
            u' OR '.join(TYPES_WITH_CONTAINING_SUBDOSSIER_INDEX)),
    ]

    with elevated_privileges():
        for batch in batched_solr_results(filters=filters, fl='UID,portal_type,path'):
            for doc in batch:
                solr.manager.connection.add({
                    "UID": doc['UID'],
                    "containing_subdossier": {"set": containing_subdossier_title},
                })


def reindex_containing_dossier_for_contained_objects(dossier, event):
    """Reindex the containging_dossier index for all the contained obects.
    """
    containing_dossier_title = dossier.Title()

    solr = queryUtility(ISolrSearch)
    filters = make_path_filter('/'.join(dossier.getPhysicalPath()), depth=-1)

    with elevated_privileges():
        for batch in batched_solr_results(filters=filters, fl='UID,portal_type,path'):
            for doc in batch:
                solr.manager.connection.add({
                    "UID": doc['UID'],
                    "containing_dossier": {"set": containing_dossier_title},
                })
                if doc['portal_type'] == 'opengever.task.task':
                    obj = OGSolrDocument(doc).getObject()
                    sync_task(obj, event)


def reindex_contained_objects(dossier, event):
    """When a dossier is modified, if the title has changed we reindex
    the corresponding index in all contained object (containing_dossier or
    containing_subdossier)
    """
    if ILocalrolesModifiedEvent.providedBy(event) or \
       IContainerModifiedEvent.providedBy(event):
        return

    attrs = tuple(
        attr
        for descr in event.descriptions
        for attr in descr.attributes
    )
    if 'IOpenGeverBase.title' not in attrs:
        return

    if dossier.is_subdossier():
        reindex_containing_subdossier_for_contained_objects(dossier, event)
    else:
        reindex_containing_dossier_for_contained_objects(dossier, event)


def reindex_blocked_local_roles(dossier, event):
    """Reindex blocked_local_roles upon the acquisition blockedness changing."""
    dossier.reindexObject(idxs=['blocked_local_roles'])


def purge_reference_number_mappings(copied_dossier, event):
    """Reset the reference number mapping when copying (or actually pasting)
    dossiers.
    """
    prefix_adapter = IReferenceNumberPrefix(copied_dossier)
    prefix_adapter.purge_mappings()


def move_connected_teamraum_to_main_dossier(obj, event):
    """If a dossier with linked workspaces gets moved into a dossier,
    the workspace link needs to be updated and moved to the new main dossier.
    """
    # make sure obj wasn't just created or deleted
    if not event.oldParent or not event.newParent:
        return

    if not ILinkedToWorkspace.providedBy(obj):
        return

    linked_workspaces = ILinkedWorkspaces(obj)
    linked_workspaces.move_workspace_links_to_main_dossier()


def dossier_comment_added(obj, event):
    """Dossier comments (responses) are part of the searchableText, so we need
    to reindex the searchableText if a new response is added.
    """

    obj.reindexObject(idxs='searchableText')


def set_responsible_role(obj, event):
    if not is_grant_role_manager_to_responsible_enabled():
        return

    obj.give_permissions_to_responsible()


def update_responsible_role(obj, event):
    if not is_grant_role_manager_to_responsible_enabled():
        return

    attrs = tuple(
        attr
        for descr in event.descriptions
        for attr in descr.attributes
    )
    if 'IDossier.responsible' not in attrs:
        return

    obj.give_permissions_to_responsible()
