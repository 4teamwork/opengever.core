from collective import dexteritytextindexer
from email.MIMEText import MIMEText
from five import grok
from ftw.mail import utils
from opengever.dossier import _
from plone.app.dexterity.behaviors import metadata
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form, dexterity
from z3c.form.interfaces import DISPLAY_MODE
from zope import schema
from zope.interface import Interface, alsoProvides
import email
from zope.i18n import translate
from ftw.mail import _ as ftw_mf


class IOGMailMarker(Interface):
    """Marker Interface for opengever mails."""


class IOGMail(form.Schema):
    """Opengever specific behavior,
    which add a title Field to the form."""

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


class OGMailBase(metadata.MetadataBase):

    def _get_title(self):
        return self.context.title

    def _set_title(self, value):
        """If no value is given,
        set the subject of the mail object instead."""

        if not value:
            subject = utils.get_header(self.context.msg, 'Subject')
            if subject:
                # long headers may contain line breaks with tabs.
                # replace these by a space.
                subject = subject.replace('\n\t', ' ')
                value = subject.decode('utf8')
            else:
                value = translate(
                    ftw_mf(u'no_subject', default=u'[No Subject]'),
                    context=self.context.REQUEST)

        if isinstance(value, str):
            raise ValueError('Title must be unicode.')
        self.context.title = value

    title = property(_get_title, _set_title)


class OGMailEditForm(dexterity.EditForm):
    """Standard edit form, but shows the message field only in Display Mode"""
    grok.context(IOGMailMarker)

    def updateWidgets(self):
        super(OGMailEditForm, self).updateWidgets()

        self.widgets.get('message').mode = DISPLAY_MODE
