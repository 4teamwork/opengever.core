from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import date
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.bundle.sections.constructor import IDontIssueDossierReferenceNumber
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.indexers import TYPES_WITH_CONTAINING_SUBDOSSIER_INDEX
from opengever.globalindex.handlers.task import sync_task
from opengever.globalindex.handlers.task import TaskSqlSyncer
from opengever.meeting.handlers import ProposalSqlSyncer
from opengever.task.task import ITask
from opengever.workspaceclient.interfaces import ILinkedToWorkspace
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from plone import api
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import getAdapter
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

    obj.reindexObject(idxs=['reference', 'sortable_reference'])


def reindex_containing_subdossier_for_contained_objects(dossier, event):
    """When a subdossier is modified, we update the ``containing_subdossier``
    index of all contained objects (documents, mails and tasks) so they don't
    show an outdated title in the ``subdossier`` column
    """
    catalog = api.portal.get_tool('portal_catalog')
    objects = catalog(path='/'.join(dossier.getPhysicalPath()),
                      portal_type=TYPES_WITH_CONTAINING_SUBDOSSIER_INDEX)

    for obj in objects:
        obj.getObject().reindexObject(idxs=['containing_subdossier'])


def reindex_containing_dossier_for_contained_objects(dossier, event):
    """Reindex the containging_dossier index for all the contained obects.
    """
    for brain in dossier.portal_catalog(path='/'.join(dossier.getPhysicalPath())):
        obj = brain.getObject()
        obj.reindexObject(idxs=['containing_dossier'])

        if ITask.providedBy(obj):
            sync_task(brain.getObject(), event)


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


def update_dossier_touched_date(obj, event):
    today = date.today()
    while obj and not IPloneSiteRoot.providedBy(obj):
        if IDossierMarker.providedBy(obj) and IDossier(obj).touched != today:
            IDossier(obj).touched = today
            # Prevent reindexing all indexes by indexing `UID` too.
            obj.reindexObject(idxs=['UID', 'touched'])
        obj = aq_parent(aq_inner(obj))


def update_dossier_touched_date_for_move_event(obj, event):
    """ObjectMovedEvent get dispatched to all children of the moved object
    by OFS.subscribers.dispatchObjectMovedEvent. Because, we do not want
    to set touched for all children of the moved object, we skip the update for
    the dispatched events.
    """
    if obj == event.object:
        update_dossier_touched_date(obj, event)


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
