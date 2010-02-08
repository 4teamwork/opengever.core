
"""
Mailing support for Document

"""

from email.MIMEBase import MIMEBase
from email import Encoders

from OFS.interfaces import IItem
from five import grok
from zope import component
from zope import schema
from zope.app.file.interfaces import IFile
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser.itemswidgets import MultiSelectWidget
from zope.app.publication.interfaces import IFileContent
from zope.interface import Interface
from zope.sendmail.interfaces import IMailer

from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form import form, field, button
from z3c.form import interfaces

from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.directives import dexterity
from plone.directives.form import widget
from plone.namedfile.interfaces import INamedFile
from plone.rfc822.interfaces import IPrimaryField
from plone.z3cform import layout

from ftw.sendmail.composer import HTMLComposer
from ftw.sendmail.interfaces import IEMailComposer

from opengever.document.interfaces import IAttachable, IAttachedMailComposer
from opengever.document import _

class FileAttachmentGenerator(grok.Adapter):
    """ FileAttachmentGenerator's render() method generates a list of MIMEBase
    attachment objects containing the attachments of this context
    """
    grok.implements(IAttachable)
    grok.context(IDexterityContent)

    def __call__(self, encode_base64=True,
               default_mimeType='application/octet-stream',
               default_filename=None):
        """ Creates a list of MIMEBase objects (for each attachable field)
        @param encode_base64 (True)
        @param default_mimeType ('application/octet-stream')
        @param default_filename (None)
        """
        parts = []
        for field in self.get_attachable_mail_fields():
            data = field.get(self.context)
            mimeType = default_mimeType
            filename = default_filename
            # is it a file? we need mimeType and maybe filename
            if IFileContent.providedBy(data):
                mimeType = data.contentType
                if INamedFile.providedBy(data):
                    filename = data.filename
            # create the part, set the data
            part = MIMEBase(*mimeType.split('/'))
            str_data = self.get_string_data(field, data)
            part.set_payload(str_data)
            # do encoding, if necessary
            if encode_base64:
                Encoders.encode_base64(part)
            # set the filename
            if filename:
                part.add_header('Content-Disposition',
                               'attachment; filename="%s"' % filename)
            parts.append(part)
        return parts

    def get_attachable_mail_fields(self):
        """ By default we use the primary field
        """
        primary = self.get_primary_field(self.context)
        if primary:
            return [primary]
        else:
            return []

    def get_primary_field(self, context):
        """ Returns the primary field of a object's schema
        """
        primaries = []
        for schema in iterSchemata(context):
            for name in schema.names():
                field = schema.get(name)
                if IPrimaryField.providedBy(field):
                    return field
        return None

    def get_string_data(self, field, data):
        """ Converts field data to string
        """
        if isinstance(data, unicode):
            data = data.encode('utf8')
        elif IFile.providedBy(data):
            data = data.data
        else:
            data = str(data)
        return data




class AttachedMailComposer(grok.GlobalUtility):
    """
    """
    grok.implements(IAttachedMailComposer)


    def __call__(self, message, subject, to_addresses, from_name='',
                 from_address='', stylesheet='', replyto_address='',
                 attachable_objects=[]):
        """
        @param message          (html) message
        @param subject          subject
        @param to_addresses     list of reciever email addresses
        @param from_name        sender name
        @param from_address     sender address
        @param stylesheet       css for html message
        @param replyto_address  reply-to address
        @param attachable_objects
                                list of objects which can possibly be used
                                as attachments (if the have a IAttachable
                                adapter)
        """
        mail = self.compose_html_mail(**{
                    'message' : message,
                    'subject' : subject,
                    'to_addresses' : to_addresses,
                    'from_name' : from_name,
                    'from_address' : from_address,
                    'stylesheet' : stylesheet,
                    'replyto_address' : replyto_address,
                })
        for object in attachable_objects:
            attacher = component.queryAdapter(object, IAttachable)
            if attacher:
                attacher = IAttachable(object)
                parts = attacher()
                for part in parts:
                    mail.attach(part)
        return mail

    
    def compose_html_mail(self, render_args={}, *args, **kwargs):
        """ Composes a HTML Mail with IEMailComposer utility
        """
        return HTMLComposer(*args, **kwargs).render(**render_args)



class ISendAsEmailFormSchema(Interface):
    attachments = schema.TextLine(title=u'attachments') # hidden
    receivers = schema.List(title=_(u'label_receivers', default=u'Receivers'),
                              description=_(u'help_receivers', default=u''),
                              value_type=schema.Choice(vocabulary=u'plone.principalsource.Users',),
                              required=True,
    )
    subject = schema.TextLine(title=_(u'label_subject', default=u'Subject'),
                              description=_(u'help_subject', default=u''),
                              required=True,
    )
    message = schema.Text(title=_(u'label_message', default=u'Message'),
                          description=_(u'help_message', default=u''),
                          required=True,
    )

class SendAsEmailForm(form.Form):
    fields = field.Fields(ISendAsEmailFormSchema)
    ignoreContext = True
    label = _(u'heading_send_as_email', u'Send as email')
    
    fields['receivers'].widgetFactory = CheckBoxFieldWidget
    
    @button.buttonAndHandler(_(u'button_send', default=u'Send'))
    def send_button_handler(self, action):
        data, errors = self.extractData()
        if len(errors)==0:
            attachments = self.attachments
            # get components
            composer = component.getUtility(IAttachedMailComposer)
            mailer = component.getUtility(IMailer, 'plone.smtp')
            mailer.update_settings()
            # prepare data
            receivers = data['receivers']
            to_addresses = self.get_formatted_user_addreses(receivers)
            sender_name = self.authenticated_member.getProperty('fullname')
            sender_email = self.authenticated_member.getProperty('email')
            message = data['message']
            message = self.context.portal_transforms.convert('text_to_html', 
                                                             message)
            # compose mail
            mail = composer(**{
                    'message' : message,
                    'subject' : data['subject'],
                    'to_addresses' : to_addresses,
                    'from_name' : sender_name,
                    'from_address' : sender_email,
                    'stylesheet' : '',
                    'replyto_address' : (sender_name, sender_email),
                    'attachable_objects' : attachments,
            })
            # send it
            mailer.send(mail['From'], mail['To'], mail.as_string())
            # let the user know
            info = _(u'info_mails_sent', 'Mails sent')
            IStatusMessage(self.request).addStatusMessage(info, type='info')
            # and redirect to default view
            return self.request.RESPONSE.redirect('./#documents-tab')

    @button.buttonAndHandler( _('cancel_back', default=u'Cancel') )
    def cancel_button_handler( self, action ):
        return self.request.RESPONSE.redirect('./#documents-tab')

    def updateWidgets(self):    
        super(SendAsEmailForm, self).updateWidgets()
        self.widgets['attachments'].mode = interfaces.HIDDEN_MODE
        # set attachments field
        self.widgets['attachments'].value = ';;'.join(self.get_attachment_paths())

    def get_attachment_paths(self):
        name = self.prefix + self.widgets.prefix + 'attachments'
        value = self.request.get(name, False)
        if value:
            value = value.split(';;')
            return value
        value = self.request.get('paths')
        if not value:
            raise Exception('No attachments')
        return value

    @property
    def attachments(self):
        objects = []
        paths = self.get_attachment_paths()
        for path in paths:
            objects.append(self.context.restrictedTraverse(str(path)))
        return objects

    @property
    def authenticated_member(self):
        return self.context.portal_membership.getAuthenticatedMember()

    def get_formatted_user_addreses(self, users):
        pm = self.context.portal_membership
        data = []
        for user in users:
            get = pm.getMemberById(user).getProperty
            data.append( (get('fullname'), get('email')) )
        return data

class SendAsEmail(layout.FormWrapper):
    form = SendAsEmailForm
    def get_attachments(self):
        return self.form_instance.attachments
