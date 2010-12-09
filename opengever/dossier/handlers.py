from five import grok
from Products.CMFCore.interfaces import IActionSucceededEvent
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
