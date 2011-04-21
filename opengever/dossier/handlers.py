from Acquisition import aq_inner, aq_parent
from five import grok
from Products.CMFCore.interfaces import IActionSucceededEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from opengever.dossier.behaviors.dossier import IDossierMarker


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
def reindex_contained_documents(dossier, event):
    """When a subdossier is modified, we update the ``containing_subdossier``
    index of all contained documents so they don't show a stale title in the
    ``subdossier`` column
    """
    parent = aq_parent(aq_inner(dossier))
    is_subdossier = IDossierMarker.providedBy(parent)
    if is_subdossier:
        documents = dossier.getFolderContents(
            contentFilter={'portal_type': 'opengever.document.document'})
        for doc in documents:
            doc.getObject().reindexObject(idxs=['containing_subdossier'])