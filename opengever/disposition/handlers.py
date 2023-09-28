from opengever.base.response import IResponseContainer
from opengever.disposition.activities import DispositionStateChangedActivity
from opengever.disposition.interfaces import IDuringDossierDestruction
from opengever.disposition.response import DispositionResponse
from opengever.dossier.interfaces import IDossierResolveProperties
from opengever.nightlyjobs.interfaces import INightlyJobProvider
from plone import api
from zope.component import getMultiAdapter
from zope.container.interfaces import IContainerModifiedEvent
from zope.globalrequest import getRequest
import logging


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


def dossier_state_changed(context, event):
    """Create journal PDF when dossier is offered.
    """
    if event.action == 'dossier-transition-offer':
        if not api.portal.get_registry_record(
                'journal_pdf_enabled',
                interface=IDossierResolveProperties):
            return

        # Queue nightly job for journal PDF
        provider = getMultiAdapter(
            (api.portal.get(), context.REQUEST, logging.getLogger()),
            INightlyJobProvider,
            name='create-dossier-journal-pdf')
        provider.queue_journal_pdf_job(context)
