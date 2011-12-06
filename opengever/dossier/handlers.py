from Acquisition import aq_inner, aq_parent
from OFS.interfaces import IObjectWillBeMovedEvent
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.utils import getToolByName
from five import grok
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectMovedEvent
from zope.component import getAdapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


@grok.subscribe(IDossierMarker, IObjectWillBeMovedEvent)
def set_former_reference_before_moving(obj, event):
    """ Temporarily store current reference number before
    moving the dossier."""

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
    be done after the dossier was moved."""

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
def save_reference_number(obj, event):
    """Generates a reference number, when it's not exists.
    and Save the reference number"""

    parent = aq_parent(aq_inner(obj))
    prefix_adapter = IReferenceNumberPrefix(parent)
    if not prefix_adapter.get_number(obj):
        prefix_adapter.set_number(obj)
    obj.reindexObject(idxs=['reference'])


@grok.subscribe(IDossierMarker, IActionSucceededEvent)
def deactivate_subdossiers(dossier, event):
    """deactivate all subdossiers, when the main dossier is deactivated"""

    if event.action == 'dossier-transition-deactivate':
        subdossiers = dossier.portal_catalog(
            provided_by="opengever.dossier.behaviors.dossier.IDossierMarker",
            path=dict(depth=1,
                query='/'.join(dossier.getPhysicalPath()),
            ),
            sort_on='filing_no',
        )

        wft = dossier.portal_workflow
        for subdossier in subdossiers:
            wft.doActionFor(
                subdossier.getObject(), 'dossier-transition-deactivate')


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
