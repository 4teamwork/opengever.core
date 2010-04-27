
from five import grok

from persistent.dict import PersistentDict
from zope.event import notify
from zope.app.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.i18nmessageid.message import Message
from zope.i18nmessageid import MessageFactory

from plone.versioningbehavior.utils import get_change_note
from Products.CMFCore.interfaces import IActionSucceededEvent

from ftw.journal.events.events import JournalEntryEvent
from ftw.task.task import ITask

from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import IObjectCheckedInEvent, IObjectCheckedOutEvent
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone.app.iterate.interfaces import IWorkingCopy

from ftw.journal.interfaces import IJournalizable
from opengever.journal import _
from opengever.trash.trash import ITrashedEvent, IUntrashedEvent
pmf = MessageFactory('plone')


def propper_string(value):
    if not value:
        return ''
    elif isinstance(value, Message):
        return value
    elif isinstance(value, unicode):
        return value.encode('utf8')
    else:
        return str(value)


def journal_entry_factory(context, action, title,
                          visible=True, comment=''):
    comment = comment=='' and get_change_note(context.REQUEST, '') or comment
    title = propper_string(title)
    action = propper_string(action)
    comment = propper_string(comment)
    entry = {
        'obj': context,
        'action': PersistentDict({
                'type': action,
                'title': title,
                'visible': visible,
                }),
        'comment': comment,
        }
    notify(JournalEntryEvent(**entry))


def translated_type(context):
    """
    Returns the translated type name of the context
    """
    type_name = context.portal_types.get(context.portal_type).Title()
    return _(unicode(type_name))


# ----------------------- DOSSIER -----------------------

DOSSIER_ADDED_ACTION = 'Dossier added'


@grok.subscribe(IDossierMarker, IObjectAddedEvent)
def dossier_added(context, event):
    title = _(u'label_dossier_added', default=u'Dossier added: ${title}', mapping={
            'title': context.title_or_id(),
            })
    journal_entry_factory(context, DOSSIER_ADDED_ACTION, title)
    return


DOSSIER_MODIIFED_ACTION = 'Dossier modified'
@grok.subscribe(IDossierMarker, IObjectModifiedEvent)
def dossier_modified(context, event):
    title = _(u'label_dossier_modified', default=u'Dossier modified')
    print title
    # XXX dirty
    try:
        # if we delete the working copy, we get a aq_based object and don't wanna
        # make a journal entry
        context.portal_types
    except AttributeError:
        return
    journal_entry_factory(context, DOSSIER_MODIIFED_ACTION, title, visible=False)
    return



DOSSIER_STATE_CHANGED = 'Dossier state changed'
@grok.subscribe(IDossierMarker, IActionSucceededEvent)
def dossier_state_changed(context, event):
    skip_transactions = [
        ]
    if event.action in skip_transactions:
        return
    newstate = event.workflow.transitions.get(event.action).new_state_id
    title = pmf( u'Dossier state changed to %s' % newstate )
    journal_entry_factory(context, DOSSIER_STATE_CHANGED, title)
    return



# ----------------------- DOCUMENT -----------------------

DOCUMENT_ADDED_ACTION = 'Document added'
@grok.subscribe(IDocumentSchema, IObjectAddedEvent)
def document_added(context, event):
    if IWorkingCopy.providedBy(context):
        return
    title = _(u'label_document_added', default=u'Document added: ${title}', mapping={
            'title' : context.title_or_id(),
            })
    # journal_entry for document:
    journal_entry_factory(context, DOCUMENT_ADDED_ACTION, title)
    # journal entry for parent (usually dossier)
    journal_entry_factory(context.aq_inner.aq_parent, DOCUMENT_ADDED_ACTION, title)
    return



DOCUMENT_MODIIFED_ACTION = 'Document modified'
@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def document_modified(context, event):
    title = _(u'label_document_modified', default=u'Document modified')
    # XXX dirty
    try:
        # if we delete the working copy, we get a aq_based object and don't wanna
        # make a journal entry
        context.portal_types
    except AttributeError:
        return
    journal_entry_factory(context, DOCUMENT_MODIIFED_ACTION, title, visible=False)
    journal_entry_factory(context.aq_inner.aq_parent, DOCUMENT_MODIIFED_ACTION, title)
    return



DOCUMENT_STATE_CHANGED = 'Document state changed'
@grok.subscribe(IDocumentSchema, IActionSucceededEvent)
def document_state_changed(context, event):
    skip_transactions = [
        'check_out',
        'check_in',
        ]
    if event.action in skip_transactions:
        return
    newstate = event.workflow.transitions.get(event.action).new_state_id
    title = pmf( u'Document state changed to %s' % newstate )
    journal_entry_factory(context, DOCUMENT_STATE_CHANGED, title)
    return


DOCUMENT_CHECKED_OUT = 'Document checked out'
@grok.subscribe(IDocumentSchema, IObjectCheckedOutEvent)
def document_checked_out(context, event):
    user_comment = event.comment
    title = _(u'label_document_checkout',
              default = u'Document checked out',)
    journal_entry_factory(context, DOCUMENT_CHECKED_OUT, title,
                          comment=user_comment)
    return


DOCUMENT_CHECKED_IN = 'Document checked in'
@grok.subscribe(IDocumentSchema, IObjectCheckedInEvent)
def document_checked_in(context, event):
    user_comment = event.comment
    title = _(u'label_document_checkin',
              default = u'Document checked in',)
    journal_entry_factory(context, DOCUMENT_CHECKED_IN, title,
                          comment=user_comment)
    return


# ----------------------- TASK -----------------------

TASK_ADDED_EVENT = 'Task added'
@grok.subscribe(ITask, IObjectAddedEvent)
def task_added(context, event):
    if IWorkingCopy.providedBy(context):
        return
    title = _(u'label_task_added', default=u'Task added: ${title}', mapping={
            'title' : context.title_or_id(),
            })
    # journal_entry for task:
    journal_entry_factory(context, TASK_ADDED_EVENT, title)
    # journal entry for parent (usually dossier)
    journal_entry_factory(context.aq_inner.aq_parent, TASK_ADDED_EVENT, title)
    return

TASK_MODIIFED_ACTION = 'Task modified'
@grok.subscribe(ITask, IObjectModifiedEvent)
def task_modified(context, event):
    title = _(u'label_task_modified', default=u'Task modified')
    # XXX dirty
    try:
        # if we delete the working copy, we get a aq_based object and don't wanna
        # make a journal entry
        context.portal_types
    except AttributeError:
        return
    journal_entry_factory(context, TASK_MODIIFED_ACTION, title, visible=False)
    journal_entry_factory(context.aq_inner.aq_parent, TASK_MODIIFED_ACTION, title)
    return


OBJECT_MOVE_TO_TRASH = 'Object moved to trash'
@grok.subscribe(IJournalizable, ITrashedEvent)
def document_trashed(context, event):
    title = _(u'label_to_trash', default = u'Object moved to trash: ${title}', mapping={
            'title':context.title_or_id(),
    })
    journal_entry_factory(context, OBJECT_MOVE_TO_TRASH, title)
    journal_entry_factory(context.aq_inner.aq_parent, OBJECT_MOVE_TO_TRASH, title)
    return

OBJECT_RESTORE = 'Object restore'
@grok.subscribe(IJournalizable, IUntrashedEvent)
def document_untrashed(context, event):
    title = _(u'label_restore', default = u'Object restore: ${title}', mapping={
            'title':context.title_or_id(),
    })
    journal_entry_factory(context, OBJECT_RESTORE, title)
    journal_entry_factory(context.aq_inner.aq_parent, OBJECT_RESTORE, title)
    return
