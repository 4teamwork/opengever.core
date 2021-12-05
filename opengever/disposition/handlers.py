from opengever.base.response import IResponseContainer
from opengever.disposition.activities import DispositionAddedActivity
from opengever.disposition.activities import DispositionStateChangedActivity
from opengever.disposition.interfaces import IDuringDossierDestruction
from opengever.disposition.response import DispositionResponse
from zope.container.interfaces import IContainerModifiedEvent
from zope.globalrequest import getRequest


def disposition_state_changed(context, event):
    if event.action == 'disposition-transition-appraise':
        context.finalize_appraisal()

    if event.action == 'disposition-transition-archive':
        context.mark_dossiers_as_archived()

    if event.action == 'disposition-transition-close':
        context.destroy_dossiers()
        context.remove_sip_package()

    if event.action == 'disposition-transition-appraised-to-closed':
        context.mark_dossiers_as_archived()
        context.destroy_dossiers()
        context.remove_sip_package()

    if event.action == 'disposition-transition-dispose':
        context.store_sip_package()
        context.schedule_sip_for_delivery()

    response = DispositionResponse(response_type=event.action)
    response.dossiers = [dossier.get_storage_representation() for dossier
                         in context.get_dossier_representations()]

    IResponseContainer(context).add(response)
    DispositionStateChangedActivity(context, getRequest(), response).record()


def disposition_added(context, event):
    response = DispositionResponse(response_type='added')
    response.dossiers = [dossier.get_storage_representation() for dossier
                         in context.get_dossier_representations()]

    IResponseContainer(context).add(response)
    DispositionAddedActivity(context, getRequest()).record()


def disposition_modified(context, event):
    if IContainerModifiedEvent.providedBy(event):
        return

    # Skip modified events during dossier destruction
    if IDuringDossierDestruction.providedBy(context.REQUEST):
        return

    response = DispositionResponse(response_type='edited')
    response.dossiers = [dossier.get_storage_representation() for dossier
                         in context.get_dossier_representations()]

    IResponseContainer(context).add(response)
