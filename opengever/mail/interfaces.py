from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute
from zope.interface import Interface


DEFAULT_MAIL_MAX_SIZE = 5


class IInboundMailSettings(Interface):

    sender_aliases = schema.Dict(
        title=u'Sender address aliases',
        description=u'Maps sender addresses to GEVER users. '
                    u'Inbound mails from those addresses will '
                    u'be created with the respective user.',
        key_type=schema.TextLine(title=u'Aliased from (email)'),
        value_type=schema.TextLine(title=u'Aliased to (userid)'),
    )


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


class IMailDownloadSettings(Interface):

    p7m_extension_replacement = schema.TextLine(
        title=u'p7m mail extension replacement upon mail download',
        description=u'signed/multipart mails get saved as p7m in Gever. '
                    u'Upon download the p7m extension gets replaced as it '
                    u'is not handled correctly by outlook.',
        default=u'eml',
    )


class IExtractedFromMail(Interface):
    """Used to mark documents extracted from a Mail"""
