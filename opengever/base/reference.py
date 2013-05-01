from Acquisition import aq_parent, aq_inner
from five import grok
from plone.dexterity.interfaces import IDexterityContent
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getUtility, queryAdapter

from opengever.base.interfaces import IBaseClientID
from opengever.base.interfaces import IReferenceNumber


class BasicReferenceNumber(grok.Adapter):
    """ Basic reference number adapter
    """
    grok.provides(IReferenceNumber)
    grok.context(IDexterityContent)

    def get_number(self):
        return ''

    def get_parent_number(self):
        parent = aq_parent(aq_inner(self.context))
        parentRF = queryAdapter(parent, IReferenceNumber)
        if parentRF:
            return parentRF.get_number()
        else:
            return None


class PlatformReferenceNumber(BasicReferenceNumber):
    """ Reference number generator for the plone site
    """
    grok.provides(IReferenceNumber)
    grok.context(ISiteRoot)

    def get_number(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IBaseClientID)
        return getattr(proxy, 'client_id')
