from opengever.disposition.activities import DispositionAddedActivity
from opengever.disposition.activities import DispositionStateChangedActivity
from opengever.disposition.interfaces import IDuringDossierDestruction
from opengever.disposition.interfaces import IHistoryStorage
from plone import api
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

    storage = IHistoryStorage(context)
    storage.add(event.action,
                api.user.get_current().getId(),
                context.get_dossier_representations())

    DispositionStateChangedActivity(
        context, getRequest(), storage.get_history()[0]).record()


def disposition_added(context, event):
    storage = IHistoryStorage(context)
    storage.add('added',
                api.user.get_current().getId(),
                context.get_dossier_representations())

    DispositionAddedActivity(context, getRequest()).record()
    context.register_watchers()


def disposition_modified(context, event):
    if IContainerModifiedEvent.providedBy(event):
        return

    # Skip modified events during dossier destruction
    if IDuringDossierDestruction.providedBy(context.REQUEST):
        return

    storage = IHistoryStorage(context)
    storage.add('edited',
                api.user.get_current().getId(),
                context.get_dossier_representations())
