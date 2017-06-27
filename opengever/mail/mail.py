from collective import dexteritytextindexer
from datetime import date
from datetime import datetime
from five import grok
from ftw.mail import _ as ftw_mf
from ftw.mail import utils
from ftw.mail.mail import IMail
from ftw.mail.mail import Mail
from ftw.mail.utils import get_filename
from ftw.mail.utils import remove_attachments
from opengever.base import _ as base_mf
from opengever.base.command import CreateDocumentCommand
from opengever.base.command import CreateEmailCommand
from opengever.base.model import create_session
from opengever.document.base import BaseDocumentMixin
from opengever.document.behaviors import metadata as ogmetadata
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.dossier import _ as dossier_mf
from opengever.mail import _
from opengever.mail.events import AttachmentsDeleted
from opengever.mail.interfaces import IAttachmentsDeletedEvent
from opengever.ogds.models.user import User
from plone.app.dexterity.behaviors import metadata
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import dexterity
from plone.directives import form
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.namedfile import field
from plone.namedfile.interfaces import HAVE_BLOBS
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from sqlalchemy import func
from z3c.form.interfaces import DISPLAY_MODE
from z3c.relationfield.relation import RelationValue
from zope import schema
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.event import notify
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import Attributes
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import os
import re


if HAVE_BLOBS:
    from plone.namedfile import NamedBlobFile as NamedFile
else:
    from plone.namedfile import NamedFile


MESSAGE_SOURCE_DRAG_DROP_UPLOAD = 'upload'
MESSAGE_SOURCE_MAILIN = 'mailin'
NO_SUBJECT_FALLBACK_ID = 'no_subject'
NO_SUBJECT_TITLE_FALLBACK = '[No Subject]'


IMail.setTaggedValue(FIELDSETS_KEY, [
    Fieldset('common',
             label=base_mf(u'fieldset_common', u'Common'),
             fields=[u'message'])
])


class IOGMailMarker(Interface):
    """Marker Interface for opengever mails."""


def get_message_source_vocabulary():
    terms = [
        SimpleTerm(MESSAGE_SOURCE_MAILIN,
                   title=_('label_message_source_mailin',
                           default='Mail-in')),
        SimpleTerm(MESSAGE_SOURCE_DRAG_DROP_UPLOAD,
                   title=_('label_message_source_d_n_d_upload',
                           default='Drag and drop upload')),
    ]
    return SimpleVocabulary(terms)


class IOGMail(form.Schema):
    """Opengever specific behavior,
    which add a title Field to the form.
    """

    form.fieldset(
        u'common',
        label=base_mf(u'fieldset_common', u'Common'),
        fields=[u'title', 'original_message', 'message_source'])

    form.order_before(title='message')
    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=dossier_mf(u'label_title', default=u'Title'),
        required=False,
    )

    form.mode(original_message=DISPLAY_MODE)
    form.read_permission(original_message='cmf.ManagePortal')
    form.write_permission(original_message='cmf.ManagePortal')
    original_message = field.NamedBlobFile(
        title=_(u'label_original_message',
                default=u'Raw *.msg message before conversion'),
        required=False,
    )

    form.mode(message_source=DISPLAY_MODE)
    form.read_permission(message_source='cmf.ManagePortal')
    form.write_permission(message_source='cmf.ManagePortal')
    message_source = schema.Choice(
        title=_('label_message_source',
                default='Message source'),
        source=get_message_source_vocabulary(),
        required=False,
    )

alsoProvides(IOGMail, IFormFieldProvider)


class OGMail(Mail, BaseDocumentMixin):
    """Opengever specific mail class."""

    # mail state's
    removed_state = 'mail-state-removed'
    active_state = 'mail-state-active'

    remove_transition = 'mail-transition-remove'
    restore_transition = 'mail-transition-restore'

    @Mail.title.setter
    def title(self, value):
        """Set mail title.

        Gever adds a title field for mails, so we need to override
        the setter of ftw.mail.mail.Mail and allow changing mail titles.
        """
        self._title = value

    @Mail.message.setter
    def message(self, message):
        """Override parent setter and avoid updating title.

        THe title is initialized with an event handler on object creation and
        must not be overwritten later since the user might change it.
        """
        self._message = message
        self._update_attachment_infos()
        self._reset_header_cache()

    def get_extraction_parent(self):
        """Return the parent that accepts extracted attachments."""
        return self.get_parent_dossier() or self.get_parent_inbox()

    def get_attachments(self):
        """Returns a list of dicts describing the attachements.

        Only attachments with a filename are returned.
        """
        return self.attachment_infos

    def has_attachments(self):
        """Return whether this mail has attachments."""
        return len(self.get_attachments()) > 0

    def extract_attachments_into_parent(self, positions):
        """Extract all specified attachments into the mails parent dossier or
        inbox.

        Also add a reference from all attached documents (*not* mails) to self.

        Positions must be a list of integer attachment positions. The position
        can be obtained from the attachment description returned by
        `get_attachments`.
        """
        docs = []
        for position in positions:
            docs.append(self.extract_attachment_into_parent(position))
        return docs

    def extract_attachment_into_parent(self, position):
        """Extract one specified attachment into the mails parent dossier or
        inbox.

        Also add a reference from all attached documents (*not* mails) to self.

        Position must be an integer attachment positions. The position
        can be obtained from the attachment description returned by
        `get_attachments`.
        """
        parent = self.get_extraction_parent()
        if parent is None:
            raise RuntimeError(
                "Could not find a parent dossier or inbox for "
                "{}".format(self.absolute_url()))

        data, content_type, filename = self._get_attachment_data(position)
        title = os.path.splitext(filename)[0]

        if content_type == 'message/rfc822':
            doc = CreateEmailCommand(
                parent, filename, data,
                title=title,
                content_type=content_type,
                digitally_available=True).execute()
        else:
            doc = CreateDocumentCommand(
                parent, filename, data,
                title=title,
                content_type=content_type,
                digitally_available=True).execute()

            # add a reference from the attachment to the mail
            intids = getUtility(IIntIds)
            iid = intids.getId(self)

            IRelatedDocuments(doc).relatedItems = [RelationValue(iid)]
            doc.reindexObject()

        return doc

    def delete_all_attachments(self):
        """Delete all of mail's attachments.

        The attachments will be removed from the attached message.
        """
        self._delete_attachments(self.get_attachments())

    def delete_attachments(self, positions):
        """Delete all specified attachments from the mails message.

        Positions must be a list of integer attachment positions. The position
        can be obtained from the attachment description returned by
        `get_attachments`.
        """
        attachments = [attachment for attachment in self.get_attachments()
                       if attachment.get('position') in positions]
        self._delete_attachments(attachments)

    def _delete_attachments(self, attachments):
        if not attachments:
            return

        attachment_names = [
            attachment.get('filename', '[no filename]').decode('utf-8')
            for attachment in attachments]
        positions = [attachment['position'] for attachment in attachments]

        # Flag the `message` attribute as having changed
        desc = Attributes(IAttachmentsDeletedEvent, "message")
        notify(AttachmentsDeleted(self, attachment_names, desc))

        # set the new message file
        msg = remove_attachments(self.msg, positions)
        self.message = NamedFile(
            data=msg.as_string(),
            contentType=self.message.contentType,
            filename=self.message.filename)

    def _get_attachment_data(self, pos):
        """Return a tuple: file-data, content-type and filename extracted from
        the attachment at position `pos`.
        """
        # get attachment at position pos
        attachment = None
        for i, part in enumerate(self.msg.walk()):
            if i == pos:
                attachment = part
                continue

        if not attachment:
            return None, '', ''

        # decode when it's necessary
        filename = get_filename(attachment)
        if not isinstance(filename, unicode):
            filename = filename.decode('utf-8')
        # remove line breaks from the filename
        filename = re.sub('\s{1,}', ' ', filename)

        content_type = attachment.get_content_type()
        if content_type == 'message/rfc822':
            nested_messages = attachment.get_payload()
            assert len(nested_messages) == 1, (
                'we expect that attachments with messages only contain one '
                'message per attachment.')
            data = nested_messages[0].as_string()
        else:
            data = attachment.get_payload(decode=1)

        return data, content_type, filename

    def related_items(self):
        """Mail does not support relatedItems"""
        return []

    def checked_out_by(self):
        """Mail does not support checkin/checkout.
        """
        return None

    def is_checked_out(self):
        """Mail does not support checkin/checkout.
        """
        return False

    def is_checkout_and_edit_available(self):
        """Mail does not support checkin/checkout.
        """
        return False

    def get_current_version(self):
        """Mails cannot be edited, they are read-only."""
        return 0

    def update_filename(self):
        if not self.message:
            return

        normalizer = getUtility(IIDNormalizer)
        normalized_subject = normalizer.normalize(self.title)
        self.message.filename = u'{}.eml'.format(normalized_subject)

    def get_file(self):
        return self.message

    def has_file(self):
        return self.message is not None

    def get_filename(self):
        if self.has_file():
            return self.message.filename
        return None


class OGMailBase(metadata.MetadataBase):
    """Behavior that adds a title field.

    The field value is stored on the Mail instannce.
    """

    def _get_title(self):
        return self.context.title

    def _set_title(self, value):
        self.context.title = value

    title = property(_get_title, _set_title)

    original_message = metadata.DCFieldProperty(IOGMail[
        'original_message'])
    message_source = metadata.DCFieldProperty(IOGMail[
        'message_source'])


@grok.subscribe(IOGMailMarker, IObjectCreatedEvent)
@grok.subscribe(IOGMailMarker, IObjectModifiedEvent)
def initalize_title(mail, event):
    title = IOGMail(mail).title
    if not title or title == NO_SUBJECT_FALLBACK_ID:
        subject = utils.get_header(mail.msg, 'Subject')
        if subject:
            # long headers may contain line breaks with tabs.
            # replace these by a space.
            subject = subject.replace('\n\t', ' ')
            value = subject.decode('utf8')
        else:
            value = translate(
                ftw_mf(NO_SUBJECT_FALLBACK_ID,
                       default=NO_SUBJECT_TITLE_FALLBACK.decode('utf-8')),
                context=getSite().REQUEST)

        IOGMail(mail).title = value

    mail.update_filename()


# XXX: The following two methods will be obselet if the ContactInformation
# stuff is refactered or move this method to the right place, whereever it
# belongs.

EMAILPATTERN = re.compile(
    ("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
     "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
     "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))


def extract_email(header_from):
    header_from = header_from.lower()
    match = re.findall(EMAILPATTERN, header_from)
    if len(match):
        return match[0][0]
    else:
        return header_from


def get_author_by_email(mail):
    header_from = utils.get_header(mail.msg, 'From')
    email = extract_email(header_from)

    session = create_session()
    principal = session.query(User).filter(
        func.lower(User.email) == email).first()

    if principal is None:
        return header_from.decode('utf-8')
    return u'{0} {1}'.format(principal.lastname, principal.firstname)


@grok.subscribe(IOGMailMarker, IObjectCreatedEvent)
def initialize_metadata(mail, event):
    if not ogmetadata.IDocumentMetadata.providedBy(mail):
        return

    if IObjectCopiedEvent.providedBy(event):
        return

    mail_metadata = ogmetadata.IDocumentMetadata(mail)
    date_time = datetime.fromtimestamp(utils.get_date_header(mail.msg, 'Date'))

    mail_metadata.document_date = date_time.date()
    mail_metadata.receipt_date = date.today()
    mail_metadata.document_author = get_author_by_email(mail)


class OGMailEditForm(dexterity.EditForm):
    """Standard edit form, but shows the message field only in Display Mode"""

    grok.context(IOGMailMarker)

    def updateWidgets(self):
        super(OGMailEditForm, self).updateWidgets()

        self.groups[0].fields.get('message').mode = DISPLAY_MODE
