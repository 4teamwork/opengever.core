from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.bundle.sections.constructor import IDontIssueDossierReferenceNumber
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.resolve import get_resolver
from opengever.globalindex.handlers.task import sync_task
from opengever.globalindex.handlers.task import TaskSqlSyncer
from opengever.meeting.handlers import ProposalSqlSyncer
from plone import api
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from zope.component import getAdapter
from zope.container.interfaces import IContainerModifiedEvent
from zope.lifecycleevent import IObjectRemovedEvent


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

    # setting the new number
    parent = aq_parent(aq_inner(obj))
    prefix_adapter = IReferenceNumberPrefix(parent)
    prefix_adapter.set_number(obj)

    obj.reindexObject(idxs=['reference'])


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

    # because we can't control the order of event handlers we have to sync
    # all containing tasks manually
    catalog = api.portal.get_tool('portal_catalog')
    tasks = catalog({
        'path': '/'.join(obj.getPhysicalPath()),
        'object_provides': 'opengever.task.task.ITask',
        'depth': -1})
    for task in tasks:
        TaskSqlSyncer(task.getObject(), None).sync()

    # And also proposals
    proposals = catalog({
        'path': '/'.join(obj.getPhysicalPath()),
        'object_provides': 'opengever.meeting.proposal.IProposal',
        'depth': -1})
    for proposal in proposals:
        ProposalSqlSyncer(proposal.getObject(), None).sync()

    obj.reindexObject(idxs=['reference'])


def reindex_contained_objects(dossier, event):
    """When a subdossier is modified, we update the ``containing_subdossier``
    index of all contained objects (documents, mails and tasks) so they don't
    show an outdated title in the ``subdossier`` column
    """
    if ILocalrolesModifiedEvent.providedBy(event) or \
       IContainerModifiedEvent.providedBy(event):
        return

    catalog = api.portal.get_tool('portal_catalog')
    parent = aq_parent(aq_inner(dossier))
    is_subdossier = IDossierMarker.providedBy(parent)
    if is_subdossier:
        objects = catalog(path='/'.join(dossier.getPhysicalPath()),
                          portal_type=['opengever.document.document',
                                       'opengever.task.task',
                                       'ftw.mail.mail'])
        for obj in objects:
            obj.getObject().reindexObject(idxs=['containing_subdossier'])


def reindex_containing_dossier(dossier, event):
    """Reindex the containging_dossier index for all the contained obects,
    when the title has changed.
    """
    if ILocalrolesModifiedEvent.providedBy(event) or \
       IContainerModifiedEvent.providedBy(event):
        return

    if not IDossierMarker.providedBy(aq_parent(aq_inner(dossier))):
        attrs = tuple(
            attr
            for descr in event.descriptions
            for attr in descr.attributes
            )

        if 'IOpenGeverBase.title' in attrs:
            for brain in dossier.portal_catalog(path='/'.join(dossier.getPhysicalPath())):
                brain.getObject().reindexObject(idxs=['containing_dossier'])
                if brain.portal_type in ['opengever.task.task', 'opengever.inbox.forwarding']:
                    sync_task(brain.getObject(), event)


def reindex_blocked_local_roles(dossier, event):
    """Reindex blocked_local_roles upon the acquisition blockedness changing."""
    dossier.reindexObject(idxs=['blocked_local_roles'])


def purge_reference_number_mappings(copied_dossier, event):
    """Reset the reference number mapping when copying (or actually pasting)
    dossiers.
    """
    prefix_adapter = IReferenceNumberPrefix(copied_dossier)
    prefix_adapter.purge_mappings()


def run_cleanup_jobs(dossier, event):
    if event.action != 'dossier-transition-resolve':
        return

    get_resolver(dossier).after_resolve()
