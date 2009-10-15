
"""
Mailing support for Document

"""

from email.MIMEBase import MIMEBase
from email import Encoders

from five import grok
from zope import component
from zope.app.publication.interfaces import IFileContent
from zope.app.file.interfaces import IFile

from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.namedfile.interfaces import INamedFile
from plone.rfc822.interfaces import IPrimaryField

from ftw.sendmail.composer import HTMLComposer
from ftw.sendmail.interfaces import IEMailComposer

from opengever.document.interfaces import IAttachable, IAttachedMailComposer


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
            if IAttachable.providedBy(object):
                attacher = IAttachable(object)
                parts = attacher()
                for part in parts:
                    mail.attach(part)
        return mail

    
    def compose_html_mail(self, *args, **kwargs):
        """ Composes a HTML Mail with IEMailComposer utility
        """
        composer = component.getUtility(IEMailComposer)
        return component(*args, **kargs)


