from zope import schema
from zope.interface import Interface

class IMailSettings(Interface):
    mail_domain = schema.Text(title=u"Mail Domain", default="opengever.4teamwork.ch")