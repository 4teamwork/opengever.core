from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Interface, Attribute
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


DEFAULT_MAIL_MAX_SIZE = 5


class ISendDocumentConf(Interface):
    max_size = schema.Int(
        title=u'max_size',
        description=u'Maximal Size (MB) of the Attachment',
        default=DEFAULT_MAIL_MAX_SIZE,
    )

    documents_as_links_default = schema.Bool(
        title=u'documents_as_links default_value',
        description=u'Send documents as links default value',
        default=False,
        )


class IDocumentSent(IObjectEvent):
    """Document has been sent"""

    sender = Attribute("The Mailsender")
    receiver = Attribute("The Mailreceiver")
    subject = Attribute("The Mailsubject")
    message = Attribute("The Message")
    attachments = Attribute("The Attachments")


class IAttachmentsDeletedEvent(IObjectModifiedEvent):
    """One or more attachments have been deleted from a ftw.mail.mail message.
    """

    attachments = Attribute("List of attachments that have been removed")


class IMailTabbedviewSettings(Interface):

    preview_tab_visible = schema.Bool(
        title=u'Is the preview tab in the mail tabbedview visible',
        default=True,
    )
