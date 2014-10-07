from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import IReferenceNumberFormatter
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.ogds.base.utils import get_current_admin_unit
from plone.dexterity.interfaces import IDexterityContent
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getUtility
from zope.component import queryAdapter


class BasicReferenceNumber(grok.Adapter):
    """ Basic reference number adapter
    """
    grok.provides(IReferenceNumber)
    grok.context(IDexterityContent)

    ref_type = 'basic'

    def get_number(self):
        numbers = self.get_parent_numbers()

        return self.get_active_formatter().complete_number(numbers)

    def get_active_formatter(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceNumberSettings)

        return queryAdapter(
            self.context, IReferenceNumberFormatter, name=proxy.formatter)

    def get_local_number(self):
        return ''

    def append_local_number(self, numbers):
        if not numbers.get(self.ref_type):
            numbers[self.ref_type] = []
        numbers[self.ref_type].insert(0, self.get_local_number())

    def get_parent_numbers(self):
        numbers = {}
        self.append_local_number(numbers)

        parent = self.context
        while not ISiteRoot.providedBy(parent):
            parent = aq_parent(aq_inner(parent))
            parent_reference_adapter = queryAdapter(parent, IReferenceNumber)
            if parent_reference_adapter:
                parent_reference_adapter.append_local_number(numbers)

        return numbers


class PlatformReferenceNumber(BasicReferenceNumber):
    """ Reference number generator for the plone site. The reference
    number part of a PloneSite is the current_admin_unit's abbreviation.
    """

    grok.provides(IReferenceNumber)
    grok.context(ISiteRoot)

    ref_type = 'site'

    def get_local_number(self):
        return get_current_admin_unit().abbreviation

    def get_number(self):
        return self.get_local_number()
