from opengever.disposition.interfaces import IDuringDossierDestruction
from opengever.disposition.interfaces import IHistoryStorage
from plone import api


def disposition_state_changed(context, event):
    if event.action == 'disposition-transition-appraise':
        context.finalize_appraisal()

    if event.action == 'disposition-transition-archive':
        context.mark_dossiers_as_archived()

    if event.action == 'disposition-transition-close':
        context.destroy_dossiers()

    storage = IHistoryStorage(context)
    storage.add(event.action,
                api.user.get_current().getId(),
                context.get_dossier_representations())


def disposition_added(context, event):
    storage = IHistoryStorage(context)
    storage.add('added',
                api.user.get_current().getId(),
                context.get_dossier_representations())

    context.register_watchers()


def disposition_modified(context, event):
    # Skip modified events during dossier destruction
    if IDuringDossierDestruction.providedBy(context.REQUEST):
        return

    storage = IHistoryStorage(context)
    storage.add('edited',
                api.user.get_current().getId(),
                context.get_dossier_representations())
