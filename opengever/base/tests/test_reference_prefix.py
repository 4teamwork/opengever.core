from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.testing import IntegrationTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestReferencePrefixAdapter(IntegrationTestCase):

    def setUp(self):
        super(TestReferencePrefixAdapter, self).setUp()
        self.login(self.regular_user)
        self.adapter = IReferenceNumberPrefix(self.leaf_repofolder)

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

        dossier = create(Builder('dossier').within(self.empty_repofolder))
        adapter = IReferenceNumberPrefix(self.empty_repofolder)

        self.assertEquals(u'1', adapter.get_number(dossier))

    def test_numbering_continues_after_nine(self):
        self.adapter.set_number(self.leaf_repofolder, 9)
        self.assertEquals(u'10', self.adapter.get_next_number())

    def test_numbering_supports_alphanumeric_numbers(self):
        self.adapter.set_number(self.leaf_repofolder, u'A1A15')
        self.assertEquals(u'A1A16', self.adapter.get_next_number())

    def test_set_number_assigns_a_specific_number_to_an_object(self):
        self.assertEquals(u'42',
                          self.adapter.set_number(self.leaf_repofolder, u'42'))
        self.assertEquals(u'42', self.adapter.get_number(self.leaf_repofolder))

    def test_set_number_recycles_old_numbers(self):
        self.adapter.set_number(self.leaf_repofolder, u'42')

        self.assertEquals(u'42', self.adapter.get_number(self.leaf_repofolder))
        self.assertEquals(u'42', self.adapter.set_number(self.leaf_repofolder))
        self.assertEquals(u'42', self.adapter.get_number(self.leaf_repofolder))

    def test_assigned_numbers_are_invalid(self):
        self.adapter.set_number(self.leaf_repofolder, u'3')

        self.assertTrue(self.adapter.is_valid_number(u'2'))
        self.assertTrue(self.adapter.is_valid_number(u'4'))
        self.assertFalse(self.adapter.is_valid_number(u'3'))

    def test_with_object_the_assigned_number_is_valid(self):
        self.adapter.set_number(self.leaf_repofolder, u'A9')
        self.assertTrue(self.adapter.is_valid_number(u'A9', self.leaf_repofolder))

    def test_with_object_numbers_assigned_to_other_objects_are_not_valid(self):
        self.adapter.set_number(self.leaf_repofolder, u'A9')
        self.assertFalse(self.adapter.is_valid_number(u'A9', self.empty_repofolder))

    def test_repository_and_dossier_use_a_seperate_counter(self):
        self.adapter.set_number(self.leaf_repofolder, u'234')

        repository = create(Builder('repository').within(self.leaf_repofolder))
        dossier = create(Builder('dossier').within(self.leaf_repofolder))

        self.assertEquals(u'235', self.adapter.get_next_number(repository))
        self.assertEquals(u'14', self.adapter.get_next_number(dossier))
