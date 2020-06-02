from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Interface, Attribute


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


class IMailTabbedviewSettings(Interface):

    preview_tab_visible = schema.Bool(
        title=u'Is the preview tab in the mail tabbedview visible',
        default=True,
    )


class IExtractedFromMail(Interface):
    """Used to mark documents extracted from a Mail"""
