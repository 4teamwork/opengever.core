from five import grok
from opengever.disposition.disposition import IDisposition
from opengever.disposition.interfaces import IHistoryStorage
from plone import api
from Products.CMFCore.interfaces import IActionSucceededEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


@grok.subscribe(IDisposition, IActionSucceededEvent)
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


@grok.subscribe(IDisposition, IObjectAddedEvent)
def disposition_added(context, event):
    storage = IHistoryStorage(context)
    storage.add('added',
                api.user.get_current().getId(),
                context.get_dossier_representations())


@grok.subscribe(IDisposition, IObjectModifiedEvent)
def disposition_modified(context, event):
    storage = IHistoryStorage(context)
    storage.add('edited',
                api.user.get_current().getId(),
                context.get_dossier_representations())
