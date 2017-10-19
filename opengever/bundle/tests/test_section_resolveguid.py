from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.resolveguid import DuplicateGuid
from opengever.bundle.sections.resolveguid import MissingGuid
from opengever.bundle.sections.resolveguid import MissingParent
from opengever.bundle.sections.resolveguid import ReferenceNumberNotFound
from opengever.bundle.sections.resolveguid import ResolveGUIDSection
from opengever.bundle.tests import MockBundle
from opengever.bundle.tests import MockTransmogrifier
from opengever.testing import IntegrationTestCase
from plone import api
from zope.annotation import IAnnotations
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject
import Missing


class TestResolveGUID(IntegrationTestCase):

    def setup_section(self, previous=None):
        previous = previous or []
        transmogrifier = MockTransmogrifier()
        self.bundle = MockBundle()
        IAnnotations(transmogrifier)[BUNDLE_KEY] = self.bundle

        options = {'blueprint', 'opengever.bundle.resolveguid'}

        return ResolveGUIDSection(transmogrifier, '', options, previous)

    def test_implements_interface(self):
        self.assertTrue(ISection.implementedBy(ResolveGUIDSection))
        verifyClass(ISection, ResolveGUIDSection)

        self.assertTrue(ISectionBlueprint.providedBy(ResolveGUIDSection))
        verifyObject(ISectionBlueprint, ResolveGUIDSection)

    def test_requires_guid(self):
        section = self.setup_section(
            previous=[{'foo': 1234}]
        )

        with self.assertRaises(MissingGuid):
            list(section)

    def test_prevents_duplicate_guid(self):
        section = self.setup_section(
            previous=[{'guid': 1234}, {'guid': 1234}]
        )

        with self.assertRaises(DuplicateGuid):
            list(section)

    def test_validates_parent_guid(self):
        section = self.setup_section(
            previous=[{'guid': 1234, 'parent_guid': 1337}]
        )

        with self.assertRaises(MissingParent):
            list(section)

    def test_reorders_items_parents_before_children(self):
        section = self.setup_section(previous=[
            {'guid': 3, 'parent_guid': 2},
            {'guid': 1337},
            {'guid': 2, 'parent_guid': 1},
            {'guid': 1},
            {'guid': 'qux', 'parent_guid': 1337},
        ])

        self.assertEqual([
                {'_nesting_depth': 1, 'guid': 1337},
                {'_nesting_depth': 2, 'guid': 'qux', 'parent_guid': 1337},
                {'_nesting_depth': 1, 'guid': 1},
                {'_nesting_depth': 2, 'guid': 2, 'parent_guid': 1},
                {'_nesting_depth': 3, 'guid': 3, 'parent_guid': 2},
            ],
            list(section)
        )

    def test_defines_guid_mapping_on_transmogrifier(self):
        item = {'guid': 'marvin'}
        section = self.setup_section(previous=[item])

        list(section)
        self.assertEqual(item, self.bundle.item_by_guid['marvin'])

    def test_catches_invalid_parent_reference_early(self):
        self.login(self.regular_user)

        items = [
            {'guid': 'a1',
             'parent_reference': [[7, 7], [7]]}
        ]
        section = self.setup_section(previous=items)
        with self.assertRaises(ReferenceNumberNotFound):
            list(section)

    def test_builds_list_of_all_existing_refnums(self):
        self.login(self.regular_user)

        section = self.setup_section(previous=[])
        list(section)

        catalog = api.portal.get_tool('portal_catalog')
        all_reference_numbers_in_catalog = [
            b.reference for b in catalog.unrestrictedSearchResults()
            if not b.reference == Missing.Value]

        self.assertEqual(
            set(all_reference_numbers_in_catalog),
            set(self.bundle.existing_refnums))

    def test_parent_reference_number_is_added_to_the_items(self):
        self.login(self.regular_user)

        items = [
            {'guid': 'a1',
             'parent_reference': [[1, 1], [1]]},
            {'guid': 'b1',
             'parent_reference': [[1, 1]]}
        ]
        section = self.setup_section(previous=items)
        items = list(section)

        self.assertEquals(
            [{'guid': 'a1', '_formatted_parent_refnum': u'Client1 1.1 / 1',
              'parent_reference': [[1, 1], [1]], '_nesting_depth': 1},
             {'guid': 'b1', '_formatted_parent_refnum': u'Client1 1.1',
              'parent_reference': [[1, 1]], '_nesting_depth': 1}],
            items)

    def test_items_reference_by_ref_tuple_are_has_nesting_depth_1(self):
        self.login(self.regular_user)

        items = [
            {'guid': 'a1',
             'parent_reference': [[1, 1], [1]]},
            {'guid': 'b1',
             'parent_reference': [[1, 1]]}
        ]
        section = self.setup_section(previous=items)
        items = list(section)

        self.assertEquals(
            [{'guid': 'a1', '_formatted_parent_refnum': u'Client1 1.1 / 1',
              'parent_reference': [[1, 1], [1]], '_nesting_depth': 1},
             {'guid': 'b1', '_formatted_parent_refnum': u'Client1 1.1',
              'parent_reference': [[1, 1]], '_nesting_depth': 1}],
            items)
