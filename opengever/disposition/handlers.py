from five import grok
from opengever.disposition.disposition import IDisposition
from Products.CMFCore.interfaces import IActionSucceededEvent


@grok.subscribe(IDisposition, IActionSucceededEvent)
def disposition_state_changed(context, event):
    if event.action == 'disposition-transition-appraise':
        context.finalize_appraisal()

    if event.action == 'disposition-transition-archive':
        context.mark_dossiers_as_archived()
