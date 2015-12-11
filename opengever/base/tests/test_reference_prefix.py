from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.testing import FunctionalTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestReferencePrefixAdapter(FunctionalTestCase):

    def setUp(self):
        super(TestReferencePrefixAdapter, self).setUp()

        self.repository = create(Builder('repository').titled(u'Position'))
        self.adapter = IReferenceNumberPrefix(self.repository)

    def test_numbering_starts_at_one_by_default(self):
        self.assertEquals(u'1', self.adapter.get_next_number())

    def test_numbering_starts_at_configured_value_in_registry(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceNumberSettings)
        proxy.reference_prefix_starting_point = u'0'
        self.assertEquals(u'0', self.adapter.get_next_number())

    def test_numbering_for_dossiers_starts_always_at_one(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceNumberSettings)
        proxy.reference_prefix_starting_point = u'0'

        dossier = create(Builder('dossier').within(self.repository))
        self.assertEquals(
            u'1',
            self.adapter.get_number(dossier))

    def test_numbering_continues_after_nine(self):
        self.set_numbering_base(u'9')
        self.assertEquals(u'10', self.adapter.get_next_number())

    def test_numbering_supports_alphanumeric_numbers(self):
        self.set_numbering_base(u'A1A15')
        self.assertEquals(u'A1A16', self.adapter.get_next_number())

    def test_set_number_assigns_a_specific_number_to_an_object(self):
        item = self.create_item()
        self.assertEquals(u'42', self.adapter.set_number(item, u'42'))
        self.assertEquals(u'42', self.adapter.get_number(item))

    def test_without_passing_a_number_set_number_generates_a_new_one(self):
        item = self.create_item()
        self.assertEquals(u'2', self.adapter.set_number(item))
        self.assertEquals(u'2', self.adapter.get_number(item))

    def test_non_assigned_numbers_are_valid(self):
        self.create_numbered_item(u'3')

        self.assertTrue(self.adapter.is_valid_number(u'2'))
        self.assertTrue(self.adapter.is_valid_number(u'4'))

    def test_assigned_numbers_are_invalid(self):
        self.create_numbered_item(u'2')

        self.assertFalse(self.adapter.is_valid_number(u'2'))

    def test_with_object_the_assigned_number_is_valid(self):
        item = self.create_numbered_item(u'A9')

        self.assertTrue(self.adapter.is_valid_number(u'A9', item))

    def test_with_object_numbers_assigned_to_other_objects_are_not_valid(self):
        item = self.create_numbered_item(u'A9')
        self.create_numbered_item(u'A10')

        self.assertFalse(self.adapter.is_valid_number(u'A10', item))

    def test_repository_and_dossier_use_a_seperate_counter(self):
        self.create_numbered_item(5)

        dossier = create(Builder('dossier').within(self.repository))
        repository = create(Builder('repository').within(self.repository))

        self.assertEquals(u'1', self.adapter.get_number(dossier))
        self.assertEquals(u'6', self.adapter.get_number(repository))

    def set_numbering_base(self, base):
        self.create_numbered_item(base)

    def create_numbered_item(self, number):
        item = self.create_item()
        self.adapter.set_number(item, number)
        return item

    def create_item(self):
        return create(Builder('repository').within(self.repository))
