from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Interface, Attribute
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class ISendDocumentConf(Interface):
    max_size = schema.Int(
        title=u'max_size',
        description=u'Maximal Size (MB) of the Attachment',
        default=5,
    )

    documents_as_links_default = schema.Bool(
        title=u'documents_as_links default_value',
        description=u'Send documents as links default value',
        default=False,
        )


class IDocumentSent(IObjectEvent):
    """Local Roles has been modified"""

    sender = Attribute("The Mailsender")
    receiver = Attribute("The Mailreceiver")
    subject = Attribute("The Mailsubject")
    message = Attribute("The Message")
    attachments = Attribute("The Attachments")


class IAttachmentsDeletedEvent(IObjectModifiedEvent):
    """One or more attachments have been deleted from a ftw.mail.mail message.
    """

    attachments = Attribute("List of attachments that have been removed")
