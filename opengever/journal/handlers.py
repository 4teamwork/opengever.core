from Products.CMFCore.interfaces import IActionSucceededEvent
from five import grok
from plone.dexterity.interfaces import IDexterityContent
from ftw.journal.events.events import JournalEntryEvent
from ftw.journal.interfaces import IJournalizable
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import IObjectCheckedInEvent
from opengever.document.interfaces import IObjectCheckedOutEvent
from opengever.document.interfaces import IObjectCheckoutCanceledEvent
from opengever.document.interfaces import IObjectRevertedToVersion
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.browser.participants import role_list_helper
from opengever.dossier.interfaces import IParticipationCreated
from opengever.dossier.interfaces import IParticipationRemoved
from opengever.journal import _
from opengever.tabbedview.helper import readable_ogds_author
from opengever.task.task import ITask
from opengever.trash.trash import ITrashedEvent, IUntrashedEvent
from persistent.dict import PersistentDict
from plone.app.iterate.interfaces import IWorkingCopy
from plone.app.versioningbehavior.utils import get_change_note
from zope.app.container.interfaces import IObjectAddedEvent
from zope.component import getMultiAdapter
from zope.event import notify
from zope.i18nmessageid import MessageFactory
from zope.i18nmessageid.message import Message
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from ftw.mail.mail import IMail
from zope.app.container.interfaces import IObjectMovedEvent
from OFS.interfaces import IObjectWillBeMovedEvent
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
                          visible=True, comment='', actor=None):
    portal_state = getMultiAdapter((context, context.REQUEST), name=u'plone_portal_state')
    if actor is None:
        actor = portal_state.member().getId()

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
        'actor': actor,
        'comment': comment,
        }

    if not actor == 'zopemaster':
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
    title = _(u'label_dossier_modified', default=u'Dossier modified: ${title}', mapping={
            'title': context.title_or_id(),
    })
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
    # we need to distinguish between "metadata modified"
    # and "file modified"
    file_changed = False
    metadata_changed = False
    for desc in event.descriptions:
        for attr in desc.attributes:
            if attr == 'file':
                file_changed = True
            else:
                metadata_changed = True

    if not file_changed and not metadata_changed:
        # the event shouldn't be fired in this case anyway..
        return

    if file_changed and metadata_changed:
        title = _(u'label_document_file_and_metadata_modified',
                  default=u'Changed file and metadata')
        parent_title = _(u'label_document_file_and_metadata_modified__parent',
                         default=u'Changed file and metadata of '
                         'document ${title}',
                         mapping=dict(title=context.title_or_id()))

    elif file_changed:
        title = _(u'label_document_file_modified',
                  default=u'Changed file')
        parent_title = _(u'label_document_file_modified__parent',
                         default=u'Changed file of document ${title}',
                         mapping=dict(title=context.title_or_id()))

    elif metadata_changed:
        title = _(u'label_document_metadata_modified',
                  default=u'Changed metadata')
        parent_title = _(u'label_document_metadata_modified__parent',
                         default=u'Changed metadata of document ${title}',
                         mapping=dict(title=context.title_or_id()))

    journal_entry_factory(context, DOCUMENT_MODIIFED_ACTION,
                          title, visible=False)
    journal_entry_factory(context.aq_inner.aq_parent,
                          DOCUMENT_MODIIFED_ACTION, parent_title)



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


DOCUMENT_CHECKOUT_CANCEL = 'Canceled document checkout'
@grok.subscribe(IDocumentSchema, IObjectCheckoutCanceledEvent)
def document_checkout_canceled(context, event):
    title = _(u'label_document_checkout_cancel',
              default=u'Canceled document checkout')
    journal_entry_factory(context, DOCUMENT_CHECKOUT_CANCEL, title)


DOCUMENT_FILE_REVERTED = 'Reverted document file'
@grok.subscribe(IDocumentSchema, IObjectRevertedToVersion)
def document_file_reverted(context, event):
    try:
        create = event.create_version
    except AttributeError:
        return
    else:
        if not create:
            return

    title = _(u'label_document_file_reverted',
              default=u'Reverte document file to version ${version_id}',
              mapping=dict(version_id=event.version_id))
    journal_entry_factory(context, DOCUMENT_FILE_REVERTED, title)



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
    title = _(u'label_task_modified', default=u'Task modified: ${title}', mapping={
            'title': context.title_or_id(),
    })
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


# ----------------------- DOSSIER PARTICIPATION -----------------------


PARTICIPANT_ADDED = 'Participant added'
@grok.subscribe(IDossierMarker, IParticipationCreated)
def participation_created(context, event):
    title = _(u'label_participant_added',
              default=u'Participant added: ${contact} with '
              'roles ${roles}',
              mapping={
            'contact' : readable_ogds_author(event.participant,
                                             event.participant.contact),
            'roles' : role_list_helper(event.participant,
                                       event.participant.roles),
            })

    journal_entry_factory(context, PARTICIPANT_ADDED, title)


PARTICIPANT_REMOVED = 'Participant removed'
@grok.subscribe(IDossierMarker, IParticipationRemoved)
def participation_removed(context, event):
    title = _(u'label_participant_removed',
              default=u'Participant removed: ${contact}',
              mapping={
            'contact' : readable_ogds_author(event.participant,
                                             event.participant.contact),
            })

    journal_entry_factory(context, PARTICIPANT_REMOVED, title)


#------------------------ Mail -----------------------------------------


MAIL_ADDED_EVENT = 'Mail added'
@grok.subscribe(IMail, IObjectAddedEvent)
def mail_added(context, event):
    title = _(u'label_mail_added',
              default=u'Mail added: ${title}',
              mapping={
              'title' : context.title_or_id()
              })
    journal_entry_factory(context.aq_inner.aq_parent, MAIL_ADDED_EVENT, title)
    return



#----------------------------Verschieben-----------------------------------


OBJECT_MOVED_EVENT = 'Object moved'
@grok.subscribe(IDexterityContent, IObjectMovedEvent)
def object_moved(context, event):
    title = _(u'label_object_moved',
                default=u'Object moved: ${title}',
                mapping={
                'title': context.title_or_id()
                })
    journal_entry_factory(context.aq_inner.aq_parent, OBJECT_MOVED_EVENT, title)
    return

OBJECT_WILL_BE_MOVED_EVENT = 'Object cut'
@grok.subscribe(IDexterityContent,IObjectWillBeMovedEvent)
def object_will_be_moved(context, event):
    title = _(u'label_object_cut',
                default=u'Object cut: ${title}',
                mapping={
                'title': context.title_or_id()
                })
    journal_entry_factory(context.aq_inner.aq_parent, OBJECT_MOVED_EVENT, title)
    return