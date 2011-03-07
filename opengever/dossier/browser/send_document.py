from zope.interface import Interface
from zope import schema
from zope.component import getUtility, provideAdapter
from zope.interface import invariant, Invalid

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate
from email import Encoders

from opengever.base.source import DossierPathSourceBinder
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from plone.z3cform import layout
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList
from z3c.form import form, button, field, validator
from z3c.form.interfaces import INPUT_MODE


from opengever.dossier import _
from opengever.dossier.validators import DocumentSizeValidator, \
    AddressValidator
from opengever.ogds.base.interfaces import IContactInformation
from opengever.inbox.interfaces import ISendable


class NoMail(Invalid):
    """ The No Mail was defined Exception."""
    __doc__ = _(u"No Mail Address")


class ISendDocumentSchema(Interface):
    """ The Send Document Form Schema."""

    intern_receiver = schema.Tuple(
        title=_('intern_receiver', default="Intern receiver"),
        description=_('help_intern_receiver', default="Live Search: search for users and contacts"),

        value_type=schema.Choice(title=_(u"mails"),
        source=u'opengever.ogds.base.EmailContactsAndUsersVocabulary'),
        required=False,
        missing_value=(), # important!
    )

    extern_receiver = schema.List(
        title=_('extern_receiver', default="Extern receiver"),
        description=_('help_extern_receiver',
            default="email addresses of the receivers. Enter manually the addresses, one per each line."),
        value_type=schema.TextLine(title=_('receiver'), ),
        required=False,
    )

    subject = schema.TextLine(
        title=_(u'label_subject', default=u'Subject'),
        description=_(u'help_subject', default=u''),
        required=True,
    )

    message = schema.Text(
        title=_(u'label_message', default=u'Message'),
        description=_(u'help_message', default=u''),
        required=True,
    )

    documents = RelationList(
        title=_(u'label_documents', default=u'Documents'),
        default=[],
        value_type=RelationChoice(
            title=u"Documents",
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'object_provides':
                        ['opengever.dossier.behaviors.dossier.IDossierMarker',
                         'opengever.document.document.IDocumentSchema',
                         'ftw.mail.mail.IMail',]
                    }),
            ),
        required=False,
        )

    @invariant
    def validateHasEmail(data):
        """ check if minium one e-mail-address is given."""
        if len(data.intern_receiver) == 0 and not data.extern_receiver:
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

provideAdapter(DocumentSizeValidator)
provideAdapter(AddressValidator)


class SendDocumentForm(form.Form):
    """ The Send Documents per Mail Formular """

    fields = field.Fields(ISendDocumentSchema)
    ignoreContext = True
    label = _('heading_send_as_email', default="Send as email")

    fields['extern_receiver'].widgetFactory[INPUT_MODE] \
        = TextLinesFieldWidget
    fields['intern_receiver'].widgetFactory[INPUT_MODE] \
        = AutocompleteMultiFieldWidget

    def update(self):
        """ put default value for documents field, into the request,

        because this view would call from the document tab in the dossier view

        """
        paths = self.request.get('paths', [])
        if paths:
            utool = getToolByName(self.context, 'portal_url')
            portal_path = utool.getPortalPath()
            # paths have to be relative to the portal
            paths = [path[len(portal_path):] for path in paths]
            self.request.set('form.widgets.documents', paths)
        super(SendDocumentForm, self).update()

    @button.buttonAndHandler(_(u'button_send', default=u'Send'))
    def send_button_handler(self, action):
        """ create and Send the Email """
        data, errors = self.extractData()
        if len(errors) == 0:
            mh = getToolByName(self.context, 'MailHost')
            contact_info = getUtility(IContactInformation)
            userid = self.context.portal_membership.getAuthenticatedMember()
            userid = userid.getId()
            intern_receiver = data.get('intern_receiver') or ()
            extern_receiver = data.get('extern_receiver') or ()

            addresses = intern_receiver + tuple(extern_receiver)

            # create the mail
            msg = self.create_mail(data.get('message'), data.get('documents'))
            msg['Subject'] = Header(data.get('subject'), 'iso-8859-1')
            sender_address = contact_info.get_email(userid)
            if not sender_address:
                sender_address = self.context.portal_url.getPortalObject().email_from_address

            msg['From'] = Header(u'%s <%s>' % (
                    contact_info.describe(userid),
                    sender_address,
                    ),
                'iso-8859-1')

            header_to = Header(','.join(addresses), 'iso-8859-1')
            msg['To'] = header_to

            # send it
            mh.send(msg, mto=','.join(addresses))

            # let the user know that the mail was sent
            info = _(u'info_mails_sent', 'Mails sent')
            IStatusMessage(self.request).addStatusMessage(info, type='info')
            # and redirect to default view / tab
            return self.request.RESPONSE.redirect('./#documents-tab')

    @button.buttonAndHandler(_('cancel_back', default=u'Cancel'))
    def cancel_button_handler(self, action):
        return self.request.RESPONSE.redirect('./#documents-tab')

    def create_mail(self, text='', docs=[]):
        """ create the mail with the attached files """
        msg = MIMEMultipart()
        msg['Date'] = formatdate(localtime=True)

        # iterate over document list and attach the file to the mail
        docs_links = u'Dokumente:\r\n'
        for doc in docs:
            if not doc.file:
                docs_links = '%s\r\n - %s (%s)' % (docs_links, doc.title, doc.absolute_url())
                continue
            docfile = doc.file
            docs_links = '%s\r\n - %s (siehe Anhang)' % (docs_links, doc.title)
            part = MIMEBase('application', docfile.contentType)
            part.set_payload(docfile.data)
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"'
                       % docfile.filename)
            msg.attach(part)

        text = '%s\r\n\r\n%s' % (text, docs_links)
        if not isinstance(text, unicode):
            text = text.decode('utf8')
        msg.attach(MIMEText(text, 'plain', 'iso-8859-1'))

        return msg


class SendDocumentFormView(layout.FormWrapper, grok.CodeView):
    """ The View wich display the SendDocument-Form.

    For sending documents with per mail.

    """

    grok.context(ISendable)
    grok.name('send_documents')
    grok.require('zope2.View')
    form = SendDocumentForm

    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.CodeView.__init__(self, context, request)
