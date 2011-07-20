from zope import schema
from zope.interface import Interface


class IMailSettings(Interface):
    mail_domain = schema.TextLine(
        title=u"Mail domain",
        description=u'Enter the mail domain which will be used \
            for sending mails into this site.',
        default=u'opengever.4teamwork.ch')


class ISendableDocsContainer(Interface):
    """Marker interface which states that the `send_documents` action is
    callable on this container type.
    """


class ISendDocumentConf(Interface):
    max_size = schema.Int(
        title=u'max_size',
        description=u'Maximal Size (MB) of the Attachment',
        default=5,
    )