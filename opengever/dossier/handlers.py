from Acquisition import aq_inner, aq_parent
from five import grok
from OFS.interfaces import IObjectWillBeMovedEvent
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from opengever.globalindex.handlers.task import sync_task
from opengever.globalindex.handlers.task import TaskSqlSyncer
from plone import api
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.utils import getToolByName
from zope.component import getAdapter
from zope.lifecycleevent import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent


@grok.subscribe(IDossierMarker, IObjectWillBeMovedEvent)
def set_former_reference_before_moving(obj, event):
    """ Temporarily store current reference number before
    moving the dossier.
    """

    # make sure obj wasn't just created or deleted
    if not event.oldParent or not event.newParent:
        return

    repr = IDossier(obj)
    ref_no = getAdapter(obj, IReferenceNumber).get_number()
    IDossier['temporary_former_reference_number'].set(repr, ref_no)


@grok.subscribe(IDossierMarker, IObjectMovedEvent)
def set_former_reference_after_moving(obj, event):
    """ Use the (hopefully) stored former reference number
    as the real new former reference number. This has to
    be done after the dossier was moved.

    """
    # make sure obj wasn't just created or deleted
    if not event.oldParent or not event.newParent:
        return

    repr = IDossier(obj)
    former_ref_no = repr.temporary_former_reference_number
    IDossier['former_reference_number'].set(repr, former_ref_no)
    # reset temporary former reference number
    IDossier['temporary_former_reference_number'].set(repr, '')

    # setting the new number
    parent = aq_parent(aq_inner(obj))
    prefix_adapter = IReferenceNumberPrefix(parent)
    prefix_adapter.set_number(obj)

    obj.reindexObject(idxs=['reference'])


@grok.subscribe(IDossierMarker, IObjectAddedEvent)
@grok.subscribe(IDossierMarker, IObjectMovedEvent)
def save_reference_number_prefix(obj, event):
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
        'path':'/'.join(obj.getPhysicalPath()),
        'object_provides': 'opengever.task.task.ITask',
        'depth':-1})
    for task in tasks:
        TaskSqlSyncer(task.getObject(), None).sync()

    obj.reindexObject(idxs=['reference'])


@grok.subscribe(IDossierMarker, IObjectModifiedEvent)
def reindex_contained_objects(dossier, event):
    """When a subdossier is modified, we update the ``containing_subdossier``
    index of all contained objects (documents, mails and tasks) so they don't
    show an outdated title in the ``subdossier`` column
    """

    catalog = getToolByName(dossier, 'portal_catalog')
    parent = aq_parent(aq_inner(dossier))
    is_subdossier = IDossierMarker.providedBy(parent)
    if is_subdossier:
        objects = catalog(path='/'.join(dossier.getPhysicalPath()),
                          portal_type=['opengever.document.document',
                                       'opengever.task.task',
                                       'ftw.mail.mail'])
        for obj in objects:
            obj.getObject().reindexObject(idxs=['containing_subdossier'])


@grok.subscribe(IDossierMarker, IObjectModifiedEvent)
def reindex_containing_dossier(dossier, event):
    """Reindex the containging_dossier index for all the contained obects,
    when the title has changed."""
    if not IDossierMarker.providedBy(aq_parent(aq_inner(dossier))):
        for descr in event.descriptions:
            for attr in descr.attributes:
                if attr == 'IOpenGeverBase.title':
                    for brain in dossier.portal_catalog(
                        path='/'.join(dossier.getPhysicalPath())):

                        brain.getObject().reindexObject(
                            idxs=['containing_dossier'])

                        if brain.portal_type in ['opengever.task.task',
                            'opengever.inbox.forwarding']:
                            sync_task(brain.getObject(), event)


@grok.subscribe(IDossierMarker, IActionSucceededEvent)
def run_cleanup_jobs(dossier, event):
    if event.action != 'dossier-transition-resolve':
        return

    DossierResolver(dossier).after_resolve_jobs()
