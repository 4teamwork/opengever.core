from zope import schema
from zope.interface import Interface

class IMailDomain(Interface):
    maildomain = schema.Text(title=u"maildomain", default="")