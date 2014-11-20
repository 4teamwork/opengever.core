from Acquisition import aq_inner, aq_parent
from five import grok
from ftw.journal.events.events import JournalEntryEvent
from ftw.journal.interfaces import IJournalizable
from ftw.mail.mail import IMail
from OFS.interfaces import IObjectWillBeMovedEvent, IObjectWillBeAddedEvent
from opengever.base.behaviors import classification
from opengever.document.behaviors import IBaseDocument
from opengever.document.interfaces import IFileCopyDownloadedEvent
from opengever.document.interfaces import IObjectCheckedInEvent
from opengever.document.interfaces import IObjectCheckedOutEvent
from opengever.document.interfaces import IObjectCheckoutCanceledEvent
from opengever.document.interfaces import IObjectRevertedToVersion
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.browser.participants import role_list_helper
from opengever.dossier.interfaces import IParticipationCreated
from opengever.dossier.interfaces import IParticipationRemoved
from opengever.journal import _
from opengever.mail.interfaces import IAttachmentsDeletedEvent
from opengever.mail.interfaces import IDocumentSent
from opengever.repository.events import IRepositoryPrefixUnlocked
from opengever.repository.repositoryfolder import IRepositoryFolderSchema
from opengever.repository.repositoryroot import IRepositoryRoot
from opengever.sharing.behaviors import IStandard
from opengever.sharing.browser.sharing import ROLE_MAPPING
from opengever.sharing.interfaces import ILocalRolesAcquisitionActivated
from opengever.sharing.interfaces import ILocalRolesAcquisitionBlocked
from opengever.sharing.interfaces import ILocalRolesModified
from opengever.tabbedview.helper import readable_ogds_author
from opengever.task.task import ITask
from opengever.trash.trash import ITrashedEvent, IUntrashedEvent
from persistent.dict import PersistentDict
from plone.app.versioningbehavior.utils import get_change_note
from plone.dexterity.interfaces import IDexterityContent
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectMovedEvent
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.i18nmessageid.message import Message
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


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
    portal_state = getMultiAdapter(
        (context, context.REQUEST), name=u'plone_portal_state')
    if actor is None:
        actor = portal_state.member().getId()
    comment = comment == '' and get_change_note(context.REQUEST, '') or comment
    title = propper_string(title)
    action = propper_string(action)
    comment = propper_string(comment)
    entry = {
        'obj': context,
        'action': PersistentDict({'type': action,
                                  'title': title,
                                  'visible': visible}),
        'actor': actor,
        'comment': comment}

    notify(JournalEntryEvent(**entry))


def role_mapping_to_str(context, mapping):
    """Parse the given local_roles mapping to a str,
    with the help of the ROLE_MAPPING from opengever.sharing"""

    skip_roles = [u'Owner', ]

    user_roles = []
    trans_mapping = None
    for behavior, translations in ROLE_MAPPING:
        if behavior.providedBy(context):
            trans_mapping = dict(translations)
        elif behavior is IStandard:
            if not trans_mapping:
                trans_mapping = dict(translations)

    for principal, roles in mapping:
        translated_roles = []
        for role in roles:
            if role not in skip_roles:
                translated_roles.append(
                    translate(
                        trans_mapping.get(role), context=context.REQUEST))

        if len(translated_roles):
            user_roles.append(
                '%s: %s' % (principal, ', '.join(translated_roles)))

    return '; '.join(user_roles)


def translated_type(context):
    """
    Returns the translated type name of the context
    """
    type_name = context.portal_types.get(context.portal_type).Title()
    return _(unicode(type_name))


# ----------------------- REPOSITORYFOLDER --------------

def get_repository_root(context):
    while not IRepositoryRoot.providedBy(context) \
            and not IPloneSiteRoot.providedBy(context):
        context = aq_parent(aq_inner(context))
    return context


LOCAL_ROLES_AQUISITION_BLOCKED = 'Local roles Aquisition Blocked'


@grok.subscribe(IRepositoryFolderSchema, IRepositoryPrefixUnlocked)
def repository_prefix_unlock(context, event):
    title = _(u'label_prefix_unlocked',
              default=u'Unlocked prefix ${prefix} in ${repository}.',
              mapping={'prefix': event.prefix,
                       'repository': context.title_or_id()})

    journal_entry_factory(
        get_repository_root(context),
        REPOSITORY_PREFIX_UNLOCKED,
        title=title)

REPOSITORY_PREFIX_UNLOCKED = 'Repository prefix unlocked'


@grok.subscribe(IRepositoryFolderSchema, ILocalRolesAcquisitionBlocked)
def repositoryfolder_local_roles_acquisition_blocked(context, event):
    title = _(u'label_local_roles_acquisition_blocked_at',
              default=u'Local roles aquistion blocked at ${repository}.',
              mapping={'repository': context.title_or_id(), })

    journal_entry_factory(
        get_repository_root(context),
        LOCAL_ROLES_AQUISITION_BLOCKED,
        title=title)

    return


LOCALROLES_AQUISITION_ACTIVATED = 'Local roles Aquisition Activated'


@grok.subscribe(IRepositoryFolderSchema, ILocalRolesAcquisitionActivated)
def repositoryfolder_local_roles_acquisition_activated(context, event):

    title = _(u'label_local_roles_acquisition_activated_at',
              default=u'Local roles aquistion activated at ${repository}.',
              mapping={'repository': context.title_or_id(), })

    journal_entry_factory(
        get_repository_root(context),
        LOCALROLES_AQUISITION_ACTIVATED,
        title=title)

    return


LOCAL_ROLES_MODIFIED = 'Local roles modified'


@grok.subscribe(IRepositoryFolderSchema, ILocalRolesModified)
def repositoryfolder_local_roles_modified(context, event):

    title = _(u'label_local_roles_modified_at',
              default=u'Local roles modified at ${repository}.',
              mapping={'repository': context.title_or_id(), })

    journal_entry_factory(
        get_repository_root(context),
        LOCAL_ROLES_MODIFIED,
        title=title,
        comment=role_mapping_to_str(context, event.new_local_roles))

    return


# ----------------------- DOSSIER -----------------------

DOSSIER_ADDED_ACTION = 'Dossier added'


@grok.subscribe(IDossierMarker, IObjectAddedEvent)
def dossier_added(context, event):
    title = _(
        u'label_dossier_added',
        default=u'Dossier added: ${title}',
        mapping={'title': context.title_or_id(), })
    journal_entry_factory(context, DOSSIER_ADDED_ACTION, title)
    return


DOSSIER_MODIIFED_ACTION = 'Dossier modified'


@grok.subscribe(IDossierMarker, IObjectModifiedEvent)
def dossier_modified(context, event):
    title = _(
        u'label_dossier_modified',
        default=u'Dossier modified: ${title}',
        mapping={'title': context.title_or_id(), })
    # XXX dirty
    try:
        # if we delete the working copy,
        # we get a aq_based object and don't wanna
        # make a journal entry
        context.portal_types
    except AttributeError:
        return
    journal_entry_factory(
        context, DOSSIER_MODIIFED_ACTION, title, visible=False)
    return


DOSSIER_STATE_CHANGED = 'Dossier state changed'


@grok.subscribe(IDossierMarker, IActionSucceededEvent)
def dossier_state_changed(context, event):
    skip_transactions = [
        ]
    if event.action in skip_transactions:
        return
    newstate = event.workflow.transitions.get(event.action).new_state_id
    title = pmf(u'Dossier state changed to %s' % newstate)
    journal_entry_factory(context, DOSSIER_STATE_CHANGED, title)
    return


LOCAL_ROLES_AQUISITION_BLOCKED = 'Local roles Aquisition Blocked'


@grok.subscribe(IDossierMarker, ILocalRolesAcquisitionBlocked)
def dossier_local_roles_acquisition_blocked(context, event):

    journal_entry_factory(
        context,
        LOCAL_ROLES_AQUISITION_BLOCKED,
        title=_(u'label_local_roles_acquisition_blocked',
                default=u'Local roles aquistion blocked.'))

    return


LOCAL_ROLES_AQUISITION_ACTIVATED = 'Local roles Aquisition Activated'


@grok.subscribe(IDossierMarker, ILocalRolesAcquisitionActivated)
def dossier_local_roles_acquisition_activated(context, event):

    journal_entry_factory(
        context,
        LOCAL_ROLES_AQUISITION_ACTIVATED,
        title=_(u'label_local_roles_acquisition_activated',
                default=u'Local roles aquistion activated.'))

    return


LOCAL_ROLES_MODIFIED = 'Local roles modified'


@grok.subscribe(IDossierMarker, ILocalRolesModified)
def dossier_local_roles_modified(context, event):

    journal_entry_factory(
        context,
        LOCAL_ROLES_MODIFIED,
        title=_(u'label_local_roles_modified',
                default=u'Local roles modified.'),
        comment=role_mapping_to_str(context, event.new_local_roles))

    return


DOC_PROPERTIES_UPDATED = 'DocProperties updated'


# We don't register an eventhandler but call this method directly from
# opengever.document.handlers
def doc_properties_updated(context):
    journal_entry_factory(context, DOC_PROPERTIES_UPDATED,
                          title=_(u'label_doc_properties_updated',
                                  default=u'DocProperties updated.'))


# ----------------------- MAIL -----------------------
ATTACHMENTS_DELETED_ACTION = 'Attachments deleted'

@grok.subscribe(IMail, IAttachmentsDeletedEvent)
def attachments_deleted(context, event):
    attachment_names = event.attachments
    title = _(
        u'label_attachments_deleted',
        default=u'Attachments deleted: ${filenames}',
        mapping={'filenames': ', '.join(attachment_names)})

    journal_entry_factory(context, ATTACHMENTS_DELETED_ACTION, title)
    return


# ----------------------- DOCUMENT -----------------------
DOCUMENT_ADDED_ACTION = 'Document added'


@grok.subscribe(IBaseDocument, IObjectAddedEvent)
def document_added(context, event):
    title = _(
        u'label_document_added',
        default=u'Document added: ${title}',
        mapping={'title': context.title, })
    # journal_entry for document:
    journal_entry_factory(context, DOCUMENT_ADDED_ACTION, title)
    # journal entry for parent (usually dossier)
    journal_entry_factory(
        context.aq_inner.aq_parent, DOCUMENT_ADDED_ACTION, title)
    return


DOCUMENT_MODIIFED_ACTION = 'Document modified'
PUBLIC_TRIAL_MODIFIED_ACTION = 'Public trial modified'


@grok.subscribe(IBaseDocument, IObjectModifiedEvent)
def document_modified(context, event):

    if IAttachmentsDeletedEvent.providedBy(event):
        # AttachmentsDeleted is a special kind of ObjectModified event
        # and is handled elsewhere - don't journalize it twice.
        return

    # we need to distinguish between "metadata modified", "file modified",
    # "file and metadata modified" and "public_trial modified"
    file_changed = False
    metadata_changed = False
    public_trial_changed = False

    parent = aq_parent(aq_inner(context))

    for desc in event.descriptions:
        for attr in desc.attributes:
            if attr in ('file', 'message'):
                file_changed = True
            elif attr in ('IClassification.public_trial', 'public_trial'):
                # Attribute name is different when changed through regular
                # edit form vs. edit_public_trial form, so check for both
                public_trial_changed = True
            else:
                metadata_changed = True

    if context.REQUEST.get('form.widgets.file.action', u'nochange') == u'nochange':
        file_changed = False

    if not file_changed and not metadata_changed and not public_trial_changed:
        # the event shouldn't be fired in this case anyway..
        return

    if file_changed and metadata_changed:
        title = _(u'label_document_file_and_metadata_modified',
                  default=u'Changed file and metadata')

        parent_title = _(u'label_document_file_and_metadata_modified__parent',
                         default=u'Changed file and metadata of '
                         'document ${title}',
                         mapping=dict(title=context.title_or_id()))

        journal_entry_factory(context, DOCUMENT_MODIIFED_ACTION, title)
        journal_entry_factory(parent, DOCUMENT_MODIIFED_ACTION, parent_title)

    elif file_changed:
        title = _(u'label_document_file_modified',
                  default=u'Changed file')
        parent_title = _(u'label_document_file_modified__parent',
                         default=u'Changed file of document ${title}',
                         mapping=dict(title=context.title_or_id()))

        journal_entry_factory(context, DOCUMENT_MODIIFED_ACTION, title)
        journal_entry_factory(parent, DOCUMENT_MODIIFED_ACTION, parent_title)

    elif metadata_changed:
        title = _(u'label_document_metadata_modified',
                  default=u'Changed metadata')
        parent_title = _(u'label_document_metadata_modified__parent',
                         default=u'Changed metadata of document ${title}',
                         mapping=dict(title=context.title_or_id()))
        journal_entry_factory(context, DOCUMENT_MODIIFED_ACTION, title)

        journal_entry_factory(parent, DOCUMENT_MODIIFED_ACTION, parent_title)

    # Always create a separate journal entry on document if public_trial was
    # changed
    if public_trial_changed:
        translated_terms = classification.translated_public_trial_terms(
            context, context.REQUEST)
        translated_public_trial = translated_terms[context.public_trial]
        title = _(u'label_document_public_trial_modified',
                  default=u'Public trial changed to "${public_trial}".',
                  mapping=dict(public_trial=translated_public_trial))

        journal_entry_factory(context, PUBLIC_TRIAL_MODIFIED_ACTION, title)


DOCUMENT_CHECKED_OUT = 'Document checked out'


@grok.subscribe(IBaseDocument, IObjectCheckedOutEvent)
def document_checked_out(context, event):
    user_comment = event.comment
    title = _(u'label_document_checkout',
              default=u'Document checked out', )
    journal_entry_factory(context, DOCUMENT_CHECKED_OUT, title,
                          comment=user_comment)
    return


DOCUMENT_CHECKED_IN = 'Document checked in'


@grok.subscribe(IBaseDocument, IObjectCheckedInEvent)
def document_checked_in(context, event):
    user_comment = event.comment
    title = _(u'label_document_checkin',
              default=u'Document checked in', )
    journal_entry_factory(context, DOCUMENT_CHECKED_IN, title,
                          comment=user_comment)
    return


DOCUMENT_CHECKOUT_CANCEL = 'Canceled document checkout'


@grok.subscribe(IBaseDocument, IObjectCheckoutCanceledEvent)
def document_checkout_canceled(context, event):
    title = _(u'label_document_checkout_cancel',
              default=u'Canceled document checkout')
    journal_entry_factory(context, DOCUMENT_CHECKOUT_CANCEL, title)


DOCUMENT_FILE_REVERTED = 'Reverted document file'


@grok.subscribe(IBaseDocument, IObjectRevertedToVersion)
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


FILE_COPY_DOWNLOADED = 'File copy downloaded'


@grok.subscribe(IBaseDocument, IFileCopyDownloadedEvent)
def file_copy_downloaded(context, event):
    title = _(u'label_file_copy_downloaded',
              default=u'Download copy')
    journal_entry_factory(context, FILE_COPY_DOWNLOADED, title)


DOCUMENT_SENT = 'Document Sent'


@grok.subscribe(IDexterityContent, IDocumentSent)
def document_sent(context, event):
    def make_document_event_list(context, items):
        urlstring = ''
        url_template = u'<span><a href="{}">{}{}</a></span>'
        lastindex = len(items)-1
        for i, item in enumerate(items):
            comma = '' if lastindex == i else ', '
            urlstring += url_template.format(item['url'], item['title'], comma)
        return urlstring

    id_util = getUtility(IIntIds)
    objs = []

    for intid in event.intids:
        obj = id_util.getObject(intid)
        url = obj.absolute_url()
        title = obj.Title().decode('utf-8')
        receiver = event.receiver
        message = event.message
        if isinstance(receiver, list):
            receiver = ', '.join(receiver)
        objs.append({'url': url, 'title': title})

    title = _(u'label_document_sent',
              default=u'Document sent by Mail: ${subject}',
              mapping={'subject': event.subject.decode('utf-8'), })

    comment = translate(
        _(u'label_document_sent_comment',
          default=u'Attachments: ${documents} | Receivers: ${receiver} |'
                    ' Message: ${message}',
          mapping={
                'documents': make_document_event_list(context, objs),
                'receiver': receiver.decode('utf-8'),
                'message': message.decode('utf-8'),
                }), context=context.REQUEST)
    journal_entry_factory(
        context, DOCUMENT_SENT, title, visible=True, comment=comment)


# ----------------------- TASK -----------------------

TASK_ADDED_EVENT = 'Task added'


@grok.subscribe(ITask, IObjectAddedEvent)
def task_added(context, event):
    title = _(
        u'label_task_added',
        default=u'Task added: ${title}',
        mapping={
            'title': context.title_or_id(),
            })

    # journal entry for parent (usually dossier)
    journal_entry_factory(context.aq_inner.aq_parent, TASK_ADDED_EVENT, title)
    return


TASK_MODIIFED_ACTION = 'Task modified'


@grok.subscribe(ITask, IObjectModifiedEvent)
def task_modified(context, event):
    title = _(
        u'label_task_modified',
        default=u'Task modified: ${title}',
        mapping={'title': context.title_or_id(), })
    # XXX dirty
    try:
        # if we delete the working copy,
        # we get a aq_based object and don't wanna
        # make a journal entry
        context.portal_types
    except AttributeError:
        return

    journal_entry_factory(
        context.aq_inner.aq_parent, TASK_MODIIFED_ACTION, title)
    return


OBJECT_MOVE_TO_TRASH = 'Object moved to trash'


@grok.subscribe(IJournalizable, ITrashedEvent)
def document_trashed(context, event):
    title = _(
        u'label_to_trash',
        default=u'Object moved to trash: ${title}',
        mapping={
            'title': context.title_or_id(),
            })

    journal_entry_factory(context, OBJECT_MOVE_TO_TRASH, title)
    journal_entry_factory(
        context.aq_inner.aq_parent, OBJECT_MOVE_TO_TRASH, title)
    return


OBJECT_RESTORE = 'Object restore'


@grok.subscribe(IJournalizable, IUntrashedEvent)
def document_untrashed(context, event):
    title = _(
        u'label_restore',
        default=u'Object restore: ${title}',
        mapping={
            'title': context.title_or_id(),
            })
    journal_entry_factory(context, OBJECT_RESTORE, title)
    journal_entry_factory(context.aq_inner.aq_parent, OBJECT_RESTORE, title)
    return


OBJECT_REMOVED = 'Object removed'


@grok.subscribe(IBaseDocument, IActionSucceededEvent)
def document_removed(context, event):
    if event.action == context.remove_transition:
        title = _(u'label_document_removed',
                  default=u'Document ${title} removed.',
                  mapping={'title': context.title_or_id()})

        parent = aq_parent(aq_inner(context))
        journal_entry_factory(context, OBJECT_REMOVED, title)
        journal_entry_factory(parent, OBJECT_REMOVED, title)

    return


OBJECT_RESTORED = 'Object restored'


@grok.subscribe(IBaseDocument, IActionSucceededEvent)
def document_restored(context, event):
    if event.action == context.restore_transition:
        title = _(u'label_document_restored',
                  default=u'Document ${title} restored.',
                  mapping={'title': context.title_or_id()})

        parent = aq_parent(aq_inner(context))
        journal_entry_factory(context, OBJECT_RESTORED, title)
        journal_entry_factory(parent, OBJECT_RESTORED, title)

    return


# ----------------------- DOSSIER PARTICIPATION -----------------------

PARTICIPANT_ADDED = 'Participant added'


@grok.subscribe(IDossierMarker, IParticipationCreated)
def participation_created(context, event):
    author = readable_ogds_author(event.participant,
                                  event.participant.contact)
    roles = role_list_helper(event.participant,
                             event.participant.roles)

    title = _(u'label_participant_added',
              default=u'Participant added: ${contact} with '
              'roles ${roles}',
              mapping={'contact': author,
                       'roles': roles}
              )

    journal_entry_factory(context, PARTICIPANT_ADDED, title)


PARTICIPANT_REMOVED = 'Participant removed'


@grok.subscribe(IDossierMarker, IParticipationRemoved)
def participation_removed(context, event):
    title = _(
        u'label_participant_removed',
        default=u'Participant removed: ${contact}',
        mapping={
            'contact': readable_ogds_author(
                event.participant,
                event.participant.contact),
            })

    journal_entry_factory(context, PARTICIPANT_REMOVED, title)


#----------------------------Verschieben-----------------------------------

OBJECT_MOVED_EVENT = 'Object moved'


@grok.subscribe(IDexterityContent, IObjectMovedEvent)
def object_moved(context, event):
    # Since IObjectAddedEvent subclasses IObjectMovedEvent this event
    # handler is also called for IObjectAddedEvent but we should not
    # do anything in this case.
    if IObjectAddedEvent.providedBy(event):
        return

    title = _(u'label_object_moved',
              default=u'Object moved: ${title}',
              mapping={'title': context.title_or_id()}
              )

    journal_entry_factory(
        context.aq_inner.aq_parent, OBJECT_MOVED_EVENT, title)
    return


OBJECT_WILL_BE_MOVED_EVENT = 'Object cut'


@grok.subscribe(IDexterityContent, IObjectWillBeMovedEvent)
def object_will_be_moved(context, event):
    if not IObjectWillBeAddedEvent.providedBy(event):
        title = _(u'label_object_cut',
                  default=u'Object cut: ${title}',
                  mapping={'title': context.title_or_id()}
                  )

        journal_entry_factory(
            context.aq_inner.aq_parent, OBJECT_WILL_BE_MOVED_EVENT, title)
    return
