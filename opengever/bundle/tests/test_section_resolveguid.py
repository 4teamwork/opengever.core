from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.resolveguid import DuplicateGuid
from opengever.bundle.sections.resolveguid import MissingGuid
from opengever.bundle.sections.resolveguid import MissingParent
from opengever.bundle.sections.resolveguid import ResolveGUIDSection
from opengever.bundle.tests import MockBundle
from opengever.bundle.tests import MockTransmogrifier
from opengever.testing import IntegrationTestCase
from zope.annotation import IAnnotations
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


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

    def test_defines_path_by_reference_number_mapping(self):
        self.login(self.regular_user)

        items = [
            {'guid': 'a1',
             'parent_ref_tuple': [[1, 1], [1]]},
            {'guid': 'b1',
             'parent_ref_tuple': [[1, 1]]}
        ]
        section = self.setup_section(previous=items)
        list(section)

        self.assertEqual(
            {'Client1 1.1': 'ordnungssystem/fuhrung/vertrage-und-vereinbarungen',
             'Client1 1.1 / 1': 'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1'},
            self.bundle.path_by_reference_number)

    def test_parent_reference_number_is_added_to_the_items(self):
        self.login(self.regular_user)

        items = [
            {'guid': 'a1',
             'parent_ref_tuple': [[1, 1], [1]]},
            {'guid': 'b1',
             'parent_ref_tuple': [[1, 1]]}
        ]
        section = self.setup_section(previous=items)
        items = list(section)

        self.assertEquals(
            [{'guid': 'a1', 'parent_ref_number': u'Client1 1.1 / 1',
              'parent_ref_tuple': [[1, 1], [1]], '_nesting_depth': 1},
             {'guid': 'b1', 'parent_ref_number': u'Client1 1.1',
              'parent_ref_tuple': [[1, 1]], '_nesting_depth': 1}],
            items)

    def test_items_reference_by_ref_tuple_are_has_nesting_depth_1(self):
        self.login(self.regular_user)

        items = [
            {'guid': 'a1',
             'parent_ref_tuple': [[1, 1], [1]]},
            {'guid': 'b1',
             'parent_ref_tuple': [[1, 1]]}
        ]
        section = self.setup_section(previous=items)
        items = list(section)

        self.assertEquals(
            [{'guid': 'a1', 'parent_ref_number': u'Client1 1.1 / 1',
              'parent_ref_tuple': [[1, 1], [1]], '_nesting_depth': 1},
             {'guid': 'b1', 'parent_ref_number': u'Client1 1.1',
              'parent_ref_tuple': [[1, 1]], '_nesting_depth': 1}],
            items)
