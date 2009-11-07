
from five import grok

from zope.event import notify 
from zope.app.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from plone.versioningbehavior.utils import get_change_note
from Products.CMFCore.interfaces import IActionSucceededEvent

from ftw.journal.events.events import JournalEntryEvent

from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import IObjectCheckedInEvent, IObjectCheckedOutEvent
from opengever.dossier.behaviors.dossier import IDossier 

from opengever.journal import _


def journal_entry_factory(context, action, title,
                          visible=True, comment=''):
    comment = comment=='' and get_change_note(context.REQUEST, '') or comment
    title = isinstance(title, unicode) and title.encode('utf8') or str(title)
    action = isinstance(action, unicode) and action.encode('utf8') or str(action)
    comment = isinstance(comment, unicode) and comment.encode('utf8') or str(comment)
    entry = {
            'obj' : context,
            'action' : {
                    'type' : action,
                    'title' : title,
                    'visible' : visible,
            },
            'comment' : comment,
    }
    notify(JournalEntryEvent(**entry))

def translated_type(context):
    """
    Returns the translated type name of the context
    """
    return context.portal_types.get(context.portal_type).Title()


# ----------------------- DOSSIER -----------------------

DOSSIER_ADDED_ACTION = 'Dossier added'
@grok.subscribe(IDossier, IObjectAddedEvent)
def dossier_added(context, event):
    #title = _('label_dossier_added', default='${type} added', mapping={
    #        'type' : translated_type(context),
    #})
    # XXX translations are not working in events -.-
    title = 'Dossier added'
    journal_entry_factory(context, DOSSIER_ADDED_ACTION, title)



DOSSIER_MODIIFED_ACTION = 'Dossier modified'
@grok.subscribe(IDossier, IObjectModifiedEvent)
def dossier_modified(context, event):
    #title = _('label_dossier_modified', default='${type} modified', mapping={
    #        'type' : translated_type(context),
    #})
    # XXX translations are not working in events -.-
    title = 'Dossier modified'
    journal_entry_factory(context, DOSSIER_ADDED_ACTION, title, visible=False)



DOSSIER_STATE_CHANGED = 'Dossier state changed'
@grok.subscribe(IDossier, IActionSucceededEvent)
def dossier_state_changed(context, event):
    newstate = event.workflow.transitions.get(event.action).new_state_id
    # XXX translations are not working in events -.-
    title = 'Dossier state changed to %(newstate)s (%(action)s)' % {
            'newstate' : newstate,
            'action' : event.action,
    }
    journal_entry_factory(context, DOSSIER_STATE_CHANGED, title)



# ----------------------- DOCUMENT -----------------------

DOCUMENT_ADDED_ACTION = 'Document added'
@grok.subscribe(IDocumentSchema, IObjectAddedEvent)
def document_added(context, event):
    #title = _('label_document_added', default='${type} added: ${title}', mapping={
    #        'type' : translated_type(context),
    #        'title' : context.title_or_id(),
    #})
    # XXX translations are not working in events -.-
    title = 'Document added: %(title)s' % {
        'title' : context.title_or_id(),
    }
    # journal_entry for document:
    journal_entry_factory(context, DOCUMENT_ADDED_ACTION, title)
    # journal entry for parent (usually dossier)
    journal_entry_factory(context.aq_inner.aq_parent, DOCUMENT_ADDED_ACTION, title)



DOCUMENT_MODIIFED_ACTION = 'Document modified'
@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def document_modified(context, event):
    #title = _('label_document_modified', default='${type} modified', mapping={
    #        'type' : translated_type(context),
    #})
    # XXX translations are not working in events -.-
    title = 'Document modified'
    journal_entry_factory(context, DOCUMENT_MODIIFED_ACTION, title, visible=False)



DOCUMENT_STATE_CHANGED = 'Document state changed'
@grok.subscribe(IDocumentSchema, IActionSucceededEvent)
def document_state_changed(context, event):
    newstate = event.workflow.transitions.get(event.action).new_state_id
    # XXX translations are not working in events -.-
    title = 'Document state changed to %(newstate)s (%(action)s)' % {
            'newstate' : newstate,
            'action' : event.action,
    }
    journal_entry_factory(context, DOCUMENT_STATE_CHANGED, title)



DOCUMENT_CHECKED_OUT = 'Document checked out'
@grok.subscribe(IDocumentSchema, IObjectCheckedOutEvent)
def document_checked_out(context, event):
    user_comment = event.comment
    title = 'Document checked out'
    journal_entry_factory(context, DOCUMENT_CHECKED_OUT, title,
                          comment=user_comment)


DOCUMENT_CHECKED_IN = 'Document checked in'
@grok.subscribe(IDocumentSchema, IObjectCheckedInEvent)
def document_checked_in(context, event):
    user_comment = event.comment
    title = 'Document checked in'
    journal_entry_factory(context, DOCUMENT_CHECKED_IN, title,
                          comment=user_comment)

