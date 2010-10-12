
from zope.interface import Interface
from zope.component.interfaces import IObjectEvent
from zope import schema

from plone.dexterity.interfaces import IDexterityContent

class IAttachable(Interface):
    """ IAttachable is used as interfaces for a adapter which can create
    MIMEBase attachment objects of a content.
    """

    def __call__(self, encode_base64=True,
                 default_mimeType='application/octet-stream',
                 default_filename=None):
        """ Creates a list of MIMEBase objects (for each attachable field)
        @param encode_base64 (True)
        @param default_mimeType ('application/octet-stream')
        @param default_filename (None)
        """
        pass


class IAttachedMailComposer(Interface):
    """ Marks a utility for generating a email containing
    multiple attachments from file-fields of multiple content
    type objects.
    """

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


class IObjectCheckedOutEvent(IObjectEvent):
    """ Event interface for events.ObjectCheckedOutEvent
    """
    comment = schema.Text(title=u'journal comment')


class IObjectCheckedInEvent(IObjectEvent):
    """ Event interface for events.ObjectCheckedInEvent
    """
    comment = schema.Text(title=u'journal comment')


class IObjectCheckoutCanceledEvent(IObjectEvent):
    """ Event interface for events.ObjectCheckoutCanceledEvent
    """


class IDocumentType(Interface):
    document_types = schema.List(
        title=u"Document Type",
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.document.document_types',
        ),
    )


class IDocuComposer(Interface):
    dc_original_path = schema.TextLine(title=u'dc_original_path')

    dc_rewrited_path = schema.TextLine(title=u'dc_rewrited_path')


class ISendDocumentConf(Interface):
    max_size = schema.Int(
        title=u'max_size',
        description=u'Maximal Size (MB) of the Attachment',
        default=5,
    )

