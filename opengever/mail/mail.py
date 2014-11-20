from collective import dexteritytextindexer
from datetime import date
from datetime import datetime
from email.MIMEText import MIMEText
from five import grok
from ftw.mail import _ as ftw_mf
from ftw.mail import utils
from ftw.mail.mail import IMail
from opengever.base import _ as base_mf
from opengever.base.browser.helper import get_css_class
from opengever.document.behaviors import metadata as ogmetadata
from opengever.dossier import _
from opengever.ogds.base.utils import create_session
from opengever.ogds.models.user import User
from plone.app.dexterity.behaviors import metadata
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form, dexterity
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from sqlalchemy import func
from z3c.form.interfaces import DISPLAY_MODE
from zope import schema
from zope.app.component.hooks import getSite
from zope.i18n import translate
from zope.interface import Interface, alsoProvides
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
import email
import re


IMail.setTaggedValue(FIELDSETS_KEY, [
    Fieldset('common',
             label=base_mf(u'fieldset_common', u'Common'),
             fields=[u'message'])
])


class IOGMailMarker(Interface):
    """Marker Interface for opengever mails."""


class IOGMail(form.Schema):
    """Opengever specific behavior,
    which add a title Field to the form."""

    form.fieldset(
        u'common',
        label=base_mf(u'fieldset_common', u'Common'),
        fields=[u'title'])

    form.order_before(title='message')
    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False,
    )

alsoProvides(IOGMail, IFormFieldProvider)


class OGMail(Item):
    """Opengever specific mail class."""

    @property
    def msg(self):
        """ returns an email.Message instance
        (copied from ftw.mail inheritance hasn't worked)
        """
        if self.message is not None:
            data = self.message.data
            temp_msg = email.message_from_string(data)
            if temp_msg.get('Subject') and '\n\t' in temp_msg['Subject']:
                # It's a long subject header than has been separated by
                # line break and tab - fix it
                fixed_subject = temp_msg['Subject'].replace('\n\t', ' ')
                data = data.replace(temp_msg['Subject'], fixed_subject)
            return email.message_from_string(data)
        return MIMEText('')

    def css_class(self):
        return get_css_class(self)

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


class OGMailBase(metadata.MetadataBase):

    def _get_title(self):
        return self.context.title

    def _set_title(self, value):
        """If no value is given,
        set the subject of the mail object instead."""

        self.context.title = value

    title = property(_get_title, _set_title)


@grok.subscribe(IOGMailMarker, IObjectCreatedEvent)
@grok.subscribe(IOGMailMarker, IObjectModifiedEvent)
def initalize_title(mail, event):

    if not IOGMail(mail).title:
        subject = utils.get_header(mail.msg, 'Subject')
        if subject:
            # long headers may contain line breaks with tabs.
            # replace these by a space.
            subject = subject.replace('\n\t', ' ')
            value = subject.decode('utf8')
        else:
            value = translate(
                ftw_mf(u'no_subject', default=u'[No Subject]'),
                context=getSite().REQUEST)

        IOGMail(mail).title = value
        mail.title = value


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


@grok.subscribe(IOGMailMarker, IObjectAddedEvent)
def initialize_metadata(mail, event):
    if not ogmetadata.IDocumentMetadata.providedBy(mail):
        return

    mail_metadata = ogmetadata.IDocumentMetadata(mail)

    date_time = datetime.fromtimestamp(utils.get_date_header(mail.msg, 'Date'))
    mail_metadata.document_date = date_time.date()

    mail_metadata.receipt_date = date.today()

    mail_metadata.document_author = get_author_by_email(mail)
    mail.reindexObject(idxs=['document_date',
                             'document_author',
                             'receipt_date'])


class OGMailEditForm(dexterity.EditForm):
    """Standard edit form, but shows the message field only in Display Mode"""
    grok.context(IOGMailMarker)

    def updateWidgets(self):
        super(OGMailEditForm, self).updateWidgets()

        self.groups[0].fields.get('message').mode = DISPLAY_MODE
