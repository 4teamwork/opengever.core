from collective import dexteritytextindexer
from datetime import date
from datetime import datetime
from ftw.mail import _ as ftw_mf
from ftw.mail import utils
from ftw.mail.mail import IMail
from ftw.mail.mail import Mail
from ftw.mail.utils import get_filename
from ftw.mail.utils import walk
from opengever.base import _ as base_mf
from opengever.base.command import CreateDocumentCommand
from opengever.base.command import CreateEmailCommand
from opengever.base.model import create_session
from opengever.base.model.favorite import Favorite
from opengever.document.base import BaseDocumentMixin
from opengever.document.behaviors import metadata as ogmetadata
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.dossier import _ as dossier_mf
from opengever.mail import _
from opengever.mail.exceptions import AlreadyExtractedError
from opengever.mail.exceptions import InvalidAttachmentPosition
from opengever.mail.interfaces import IExtractedFromMail
from opengever.mail.utils import is_rfc822_ish_mimetype
from opengever.ogds.models.user import User
from plone import api
from plone.app.dexterity.behaviors import metadata
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.namedfile import field
from plone.supermodel import model
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from plone.uuid.interfaces import IUUID
from sqlalchemy import func
from z3c.form.interfaces import DISPLAY_MODE
from z3c.relationfield.relation import RelationValue
from zope import schema
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import os
import re


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


class IOGMail(model.Schema):
    """Opengever specific behavior,
    which add a title Field to the form.
    """

    model.fieldset(
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
        vocabulary=get_message_source_vocabulary(),
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

    @property
    def is_mail(self):
        return True

    def get_extraction_parent(self):
        """Return the parent that accepts extracted attachments."""
        return self.get_parent_dossier() or self.get_parent_inbox()

    def get_attachments(self, unextracted_only=False):
        """Returns a list of dicts describing the attachements.

        Only attachments with a filename are returned.
        """
        if unextracted_only:
            return tuple(info for info in self.attachment_infos if not info.get('extracted'))
        return self.attachment_infos

    def has_attachments(self):
        """Return whether this mail has attachments."""
        return len(self.get_attachments()) > 0

    def _get_attachment_info(self, position):
        """Return the attachment info for attachment at given position.
        This should not be modified as it is not a persistent mapping"""
        for info in self._attachment_infos:
            if info['position'] == position:
                return info
        raise InvalidAttachmentPosition(position)

    def _modify_attachment_info(self, position, **kwargs):
        """update the info at the given position with all passed
        keyword arguments"""
        info = self._get_attachment_info(position)
        info.update(kwargs)
        self._p_changed = True
        return dict(info)

    def extract_attachments_into_parent(self, positions):
        """Extract all specified attachments into the mails parent dossier or
        inbox.

        Also add a reference from all attached documents (*not* mails) to self.

        Positions must be a list of integer attachment positions. The position
        can be obtained from the attachment description returned by
        `get_attachments`.
        """
        docs = {}
        for position in positions:
            docs[position] = self.extract_attachment_into_parent(position)
        return docs

    def extract_attachment_into_parent(self, position):
        """Extract one specified attachment into the mails parent dossier or
        inbox.

        Also add a reference from all attached documents (*not* mails) to self.

        Position must be an integer attachment positions. The position
        can be obtained from the attachment description returned by
        `get_attachments`.
        """
        info = self._get_attachment_info(position)

        if info.get('extracted'):
            raise AlreadyExtractedError(info)

        parent = self.get_extraction_parent()
        if parent is None:
            raise RuntimeError(
                "Could not find a parent dossier or inbox for "
                "{}".format(self.absolute_url()))

        data, content_type, filename = self._get_attachment_data(position)
        title = os.path.splitext(filename)[0]

        # try to guess content-type based on mimetype registry first, then
        # fall back to what is provided in the mail as second option.
        # this will consistently set the mimetype the same way as when d&d
        # uploading files and also correctly handle p7m mails.
        mtr = api.portal.get_tool('mimetypes_registry')
        mimetype = mtr.classify(data, filename=filename)
        if mimetype is not None:
            content_type = str(mimetype)

        if is_rfc822_ish_mimetype(content_type):
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
            alsoProvides(doc, IExtractedFromMail)
            doc.reindexObject()

        # mark attachment as extracted
        self._modify_attachment_info(
            position, extracted=True, extracted_document_uid=IUUID(doc))

        return doc

    def _get_attachment_data(self, pos):
        """Return a tuple: file-data, content-type and filename extracted from
        the attachment at position `pos`.
        """
        # get attachment at position pos
        attachment = None
        for i, part in enumerate(walk(self.msg)):
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
        filename = re.sub(r'\s{1,}', ' ', filename)

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

    def is_collaborative_checkout(self):
        """Mail does not support checkin/checkout.
        """
        return False

    def is_checkout_and_edit_available(self):
        """Mail does not support checkin/checkout.
        """
        return False

    def is_office_connector_editable(self):
        """Mail cannot be edited with office connector
        """
        return False

    def get_current_version_id(self, missing_as_zero=False):
        """Mails cannot be edited, they are read-only."""
        return 0

    def update_filename(self):
        if not self.message:
            return

        normalizer = getUtility(IFileNameNormalizer, name='gever_filename_normalizer')
        normalized_subject = normalizer.normalize_name(self.title)
        if self.message.filename:
            ext = os.path.splitext(self.message.filename)[-1]
        else:
            ext = u'.eml'

        new_filename = u'{}{}'.format(normalized_subject, ext)
        if self.message.filename != new_filename:
            self.message.filename = new_filename
            Favorite.query.update_filename(self)

    def get_file(self):
        """An opengever mail has two fields for storing the mail-data.

        - The primary-field contains the .eml file which is either a converted
          version of a .msg-file or a directly uploaded .eml-file.

        - The original_message-field contains the original .msg-file, but only
          if the user uploaded one. This file will be used to generate the .eml-file
          for the primary-field.
        """
        return self.original_message or self.message

    def has_file(self):
        return self.message is not None

    def get_filename(self):
        if self.has_file():
            return self.get_file().filename
        return None

    def get_download_view_name(self):
        if self.original_message:
            return '@@download/original_message'
        return 'download'


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


def initialize_title(mail, event):
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
    (r"([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
     r"{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
     r"\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))


def extract_email(header_from):
    header_from = header_from.lower()
    match = re.findall(EMAILPATTERN, header_from)
    if match:
        return match[0][0]
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


def initialize_metadata(mail, event):
    if not ogmetadata.IDocumentMetadata.providedBy(mail):
        return

    if IObjectCopiedEvent.providedBy(event):
        return

    mail_metadata = ogmetadata.IDocumentMetadata(mail)
    timestamp = utils.get_date_header(mail.msg, 'Date') or 0.0
    date_time = datetime.fromtimestamp(timestamp)

    mail_metadata.document_date = date_time.date()
    mail_metadata.receipt_date = date.today()
    mail_metadata.document_author = get_author_by_email(mail)
