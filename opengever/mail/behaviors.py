from zope.interface import Interface
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryUtility
from zope.app.intid.interfaces import IIntIds
from opengever.mail.behaviors import IMailSettings

class IMailInAddress(Interface):
    def get_email_address(self):
        """ generates an email adress for a dossier
        """
        
class IMailInAddressMarker(Interface):
    pass

class IMailInAddress(Interface):
    def get_email_address(self):
        id_util = getUtility(IIntIds)
        intid = id_util.queryId(self.context)
        registry = queryUtility(IRegistry)
        proxy = registry.forInterface(IMailSettings)
        domain = getattr(proxy,'mail_domain','fehler')
        return '%s@%s' % (str(intid),domain)

