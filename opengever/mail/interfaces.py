from zope import schema
from zope.interface import Interface

class IMailSettings(Interface):
    mail_domain = schema.Text(
        title=u"Mail domain",
        description=u'Enter the mail domain which will be used \
            for sending mails into this site.',
        default=u'opengever.4teamwork.ch')