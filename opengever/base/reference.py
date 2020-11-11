from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import IReferenceNumberFormatter
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.ogds.base.utils import get_current_admin_unit
from plone.dexterity.interfaces import IDexterityContent
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryAdapter
from zope.interface import implementer


@implementer(IReferenceNumber)
@adapter(IDexterityContent)
class BasicReferenceNumber(object):
    """Basic reference number adapter."""

    ref_type = 'basic'

    def __init__(self, context):
        self.context = context

    def get_number(self):
        numbers = self.get_numbers()

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

    def get_numbers(self):
        numbers = {}
        self.append_local_number(numbers)

        parent = self.context

        while parent and not ISiteRoot.providedBy(parent):
            parent = aq_parent(aq_inner(parent))
            parent_reference_adapter = queryAdapter(parent, IReferenceNumber)

            if parent_reference_adapter:
                parent_reference_adapter.append_local_number(numbers)

        return numbers


@adapter(ISiteRoot)
class PlatformReferenceNumber(BasicReferenceNumber):
    """Reference number generator for the plone site. The reference
    number part of a PloneSite is the current_admin_unit's abbreviation.
    """

    ref_type = 'site'

    def get_local_number(self):
        return get_current_admin_unit().abbreviation

    def get_number(self):
        return self.get_local_number()
