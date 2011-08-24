from Acquisition import aq_inner, aq_parent
from five import grok
from opengever.dossier.behaviors.dossier import IDossierMarker
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.utils import getToolByName
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


@grok.subscribe(IDossierMarker, IActionSucceededEvent)
def deactivate_subdossiers(dossier, event):
    """When deactivate, it deactivate also all subdossiers """

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
            wft.doActionFor(subdossier.getObject(), 'dossier-transition-deactivate')

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
