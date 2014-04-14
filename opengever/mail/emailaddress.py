from ftw.mail.interfaces import IEmailAddress
from ftw.mail.interfaces import IMailSettings
from plone.registry.interfaces import IRegistry
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implements


class IntIdEmailAddress(object):
    implements(IEmailAddress)

    def __init__(self, request):
        self.request = request

    def get_email_for_object(self, obj, domain=None):
        if domain is None:
            registry = queryUtility(IRegistry)
            proxy = registry.forInterface(IMailSettings)
            domain = getattr(proxy, 'mail_domain', u'nodomain.com').encode(
            'utf-8')

        id_util = getUtility(IIntIds)
        intid = id_util.queryId(obj)
        return '@'.join((str(intid), domain))

    def get_object_for_email(self, email):
        intid = int(email.split('@')[0])
        id_util = getUtility(IIntIds)
        return id_util.queryObject(intid)