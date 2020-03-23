from datetime import date
from email import Encoders
from email.Header import Header
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate
from ftw.keywordwidget.widget import KeywordWidget
from ftw.mail.inbound import createMailInContainer
from opengever.base.source import DossierPathSourceBinder
from opengever.dossier.interfaces import IDossierMarker
from opengever.mail import _
from opengever.mail.events import DocumentSent
from opengever.mail.interfaces import ISendDocumentConf
from opengever.mail.utils import make_addr_header
from opengever.mail.validators import AddressValidator
from opengever.mail.validators import DocumentSizeValidator
from opengever.ogds.base.sources import AllEmailContactsAndUsersSourceBinder
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from opengever.tabbedview.utils import get_containing_document_tab_url
from plone.autoform.widgets import ParameterizedWidget
from plone.registry.interfaces import IRegistry
from plone.z3cform import layout
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form import validator
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget
from z3c.form.interfaces import INPUT_MODE
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant


CHARSET = 'utf-8'


def default_documents_as_links():
    """Set the client specific default (configured in the registry)."""
    registry = getUtility(IRegistry)
    proxy = registry.forInterface(ISendDocumentConf)
    return proxy.documents_as_links_default


class NoMail(Invalid):
    """This is a dummy class to raise an exception in the lack of a mail
    address.
    """

    __doc__ = _(u"No Mail Address")


class ISendDocumentSchema(Interface):
    """The Send Document Form Schema."""

    intern_receiver = schema.Tuple(
        title=_('intern_receiver', default="Intern receiver"),
        description=_('help_intern_receiver',
                      default="Live Search: search for users and contacts"),

        value_type=schema.Choice(
            title=_(u"mails"),
            source=AllEmailContactsAndUsersSourceBinder()),
        required=False,
        missing_value=(),  # important!
        default=(),
        )

    extern_receiver = schema.List(
        title=_('extern_receiver', default="Extern receiver"),
        description=_('help_extern_receiver',
                      default="email addresses of the receivers. "
                      "Enter manually the addresses, one per each line."),
        value_type=schema.TextLine(title=_('receiver'), ),
        required=False,
        )

    subject = schema.TextLine(
        title=_(u'label_subject', default=u'Subject'),
        required=True,
        )

    message = schema.Text(
        title=_(u'label_message', default=u'Message'),
        required=True,
        )

    documents = RelationList(
        title=_(u'label_documents', default=u'Attachments'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Documents",
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'object_provides':
                        ['opengever.dossier.behaviors.dossier.IDossierMarker',
                         'opengever.task.task.ITask',
                         'opengever.document.document.IDocumentSchema',
                         'ftw.mail.mail.IMail',
                         ]}),
            ),
        required=False,
        )

    documents_as_links = schema.Bool(
        title=_(u'label_documents_as_link',
                default=u'Send documents only als links'),
        required=True,
        defaultFactory=default_documents_as_links,
        )

    file_copy_in_dossier = schema.Bool(
        title=_(u'label_file_copy_in_dossier',
                default=u'File a copy of the sent mail in dossier'),
        required=True,
        default=True,
        )

    @invariant
    def validateHasEmail(self):
        """Check if minium one e-mail-address is given."""
        if len(self.intern_receiver) == 0 and not self.extern_receiver:
            raise NoMail(_(u'You have to select a intern \
                            or enter a extern mail-addres'))


# put the validators
validator.WidgetValidatorDiscriminators(
    DocumentSizeValidator,
    field=ISendDocumentSchema['documents'],
    )

validator.WidgetValidatorDiscriminators(
    AddressValidator,
    field=ISendDocumentSchema['extern_receiver'],
    )


class SendDocumentForm(form.Form):
    """A form to send documents over mail with."""

    fields = field.Fields(ISendDocumentSchema)
    ignoreContext = True
    label = _('heading_send_as_email', default="Send as email")

    fields['extern_receiver'].widgetFactory[INPUT_MODE] \
        = TextLinesFieldWidget
    fields['intern_receiver'].widgetFactory[INPUT_MODE] = ParameterizedWidget(
        KeywordWidget,
        async=True)

    fields['documents_as_links'].widgetFactory[INPUT_MODE] \
        = SingleCheckBoxFieldWidget

    def update(self):
        """Put default value for documents field, into the request,
        because this view would call from the document tab in the dossier view
        """
        paths = self.request.get('paths', [])
        if paths:
            self.request.set('form.widgets.documents', paths)

        super(SendDocumentForm, self).update()

    def updateWidgets(self):
        super(SendDocumentForm, self).updateWidgets()

        if not self._allow_save_file_copy_in_context():
            file_copy_widget = self.widgets['file_copy_in_dossier']
            disabled_hint_text = translate(
                _(u'file_copy_widget_disabled_hint_text',
                  default='(only possible for open dossiers)'),
                context=self.request)

            file_copy_widget.value = []
            checkbox = file_copy_widget.items[0]
            checkbox['label'] = u'{} {}'.format(
                checkbox['label'], disabled_hint_text)
            file_copy_widget.disabled = 'disabled'

    @button.buttonAndHandler(_(u'button_send', default=u'Send'))
    def send_button_handler(self, action):
        """Create and Send the Email."""
        data, errors = self.extractData()

        if len(errors) == 0:
            mh = getToolByName(self.context, 'MailHost')
            userid = self.context.portal_membership.getAuthenticatedMember()
            userid = userid.getId()
            intern_receiver = []
            for receiver in data.get('intern_receiver', []):
                # cut away the username
                intern_receiver.append(receiver.split(':')[0])

            extern_receiver = data.get('extern_receiver') or []
            addresses = intern_receiver + extern_receiver

            # create the mail
            msg = self.create_mail(
                data.get('message'),
                data.get('documents'),
                only_links=data.get('documents_as_links'))

            msg['Subject'] = Header(data.get('subject'), CHARSET)

            user = ogds_service().fetch_user(userid)
            sender_address = user and user.email
            if not sender_address:
                portal = self.context.portal_url.getPortalObject()
                sender_address = portal.email_from_address

            msg['From'] = make_addr_header(
                user.label(), sender_address, CHARSET)

            header_to = Header(','.join(addresses), CHARSET)
            msg['To'] = header_to

            # send it
            mfrom = u'{} <{}>'.format(
                user.label(), sender_address).encode(CHARSET)
            mh.send(msg, mfrom=mfrom, mto=','.join(addresses))

            # Store a copy of the sent mail in dossier
            if (data.get('file_copy_in_dossier', False)
                    and self._allow_save_file_copy_in_context()):
                self.file_sent_mail_in_dossier(msg)

            # let the user know that the mail was sent
            info = _(u'info_mail_sent', 'E-mail has been sent.')
            notify(DocumentSent(
                    self.context, userid, header_to, data.get('subject'),
                    data.get('message'), data.get('documents')))

            IStatusMessage(self.request).addStatusMessage(info, type='info')
            # and redirect to default view / tab
            return self.request.RESPONSE.redirect(
                get_containing_document_tab_url(data.get('documents')[0]))

    @button.buttonAndHandler(_('cancel_back', default=u'Cancel'))
    def cancel_button_handler(self, action):
        data, errors = self.extractData()

        if data.get('documents'):
            url = get_containing_document_tab_url(data.get('documents')[0])
        else:
            url = get_containing_document_tab_url(self.context)

        return self.request.RESPONSE.redirect(url)

    def create_mail(self, text='', objs=[], only_links=''):
        """Create the mail and attach the the files.

        For object without a file it include a Link to the Object in to the
        message.
        """
        attachment_parts = []
        msg = MIMEMultipart()
        msg['Date'] = formatdate(localtime=True)

        # iterate over object list (which can include documents and mails),
        # create attachement parts for them and prepare docs_links
        docs_links = '%s:\r\n' % (translate(
                _('label_documents', default=u'Attachments'),
                context=self.request))

        for obj in objs:
            obj_file = obj.get_file()

            if only_links or not obj_file:
                # rewrite the url with current adminunit's public url
                url = '%s/%s' % (
                    get_current_admin_unit().public_url,
                    '/'.join(obj.getPhysicalPath()[2:]))

                docs_links = '%s\r\n - %s (%s)' % (
                    docs_links, obj.title, url)
                continue

            docs_links = '%s\r\n - %s (%s)' % (
                docs_links,
                obj.title,
                translate(
                    _('label_see_attachment', default=u'see attachment'),
                    context=self.request))

            mimetype = obj_file.contentType
            if not mimetype:
                mimetype = 'application/octet-stream'
            maintype, subtype = obj_file.contentType.split('/', 1)
            part = MIMEBase(maintype, subtype)
            part.set_payload(obj_file.data)
            if mimetype != 'message/rfc822':
                Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"'
                            % obj_file.filename)
            attachment_parts.append(part)

        # First, create the text part and attach it to the message ...
        text = '%s\r\n\r\n%s\r\n' % (
            text.encode(CHARSET, 'ignore'),
            docs_links.encode(CHARSET))

        if not isinstance(text, unicode):
            text = text.decode('utf8')
        msg.attach(MIMEText(text, 'plain', CHARSET))

        # ... then attach all the attachment parts
        for part in attachment_parts:
            msg.attach(part)

        return msg

    def file_sent_mail_in_dossier(self, msg):
        dossier = self.context
        mail = createMailInContainer(dossier, msg.as_string())
        mail.delivery_date = date.today()
        mail.reindexObject(idxs=['delivery_date'])
        status_msg = _(
            u"Sent mail filed as '${title}'.",
            mapping={'title': mail.title_or_id()})
        IStatusMessage(self.request).addStatusMessage(status_msg, type='info')

    def _allow_save_file_copy_in_context(self):
        """The field file_copy_in_dossier should not be allowed for closed
        dossiers or on all other contenttypes (i.e. the Inbox).
        """
        if IDossierMarker.providedBy(self.context):
            return self.context.is_open()
        return False


class SendDocumentFormView(layout.FormWrapper):
    """The View wich display the SendDocument-Form.

    For sending documents with per mail.
    """

    form = SendDocumentForm
