from zope import schema
from zope.interface import Interface, Attribute
from zope.component.interfaces import IObjectEvent


class IMailSettings(Interface):
    mail_domain = schema.TextLine(
        title=u"Mail domain",
        description=u'Enter the mail domain which will be used \
            for sending mails into this site.',
        default=u'opengever.4teamwork.ch')


class ISendDocumentConf(Interface):
    max_size = schema.Int(
        title=u'max_size',
        description=u'Maximal Size (MB) of the Attachment',
        default=5,
    )

    documents_as_links_default = schema.Bool(
        title=u'documents_as_links default_value',
        description=u'Send documents as links default value',
        default = False,
        )


class IDocumentSent(IObjectEvent):
    """Local Roles has been modified"""

    sender = Attribute("The Mailsender")
    receiver = Attribute("The Mailreceiver")
    subject = Attribute("The Mailsubject")
    message = Attribute("The Message")
    attachments = Attribute("The Attachments")
