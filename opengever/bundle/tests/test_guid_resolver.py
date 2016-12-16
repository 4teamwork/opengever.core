from opengever.bundle.exceptions import DuplicateGUID
from opengever.bundle.exceptions import MissingGUID
from opengever.bundle.exceptions import MissingParent
from opengever.bundle.loader import GUIDResolver
from unittest2 import TestCase


class TestGUIDResolver(TestCase):

    def setup_resolver(self):
        resolver = GUIDResolver()
        return resolver

    def test_requires_guid(self):
        resolver = self.setup_resolver(
            items=[{'foo': 1234}]
        )

        with self.assertRaises(MissingGUID):
            list(resolver)

    def test_prevents_duplicate_guid(self):
        resolver = self.setup_resolver(
            items=[{'guid': 1234}, {'guid': 1234}]
        )

        with self.assertRaises(DuplicateGUID):
            list(resolver)

    def test_validates_parent_guid(self):
        resolver = self.setup_resolver(
            items=[{'guid': 1234, 'parent_guid': 1337}]
        )

        with self.assertRaises(MissingParent):
            list(resolver)

    def test_reorders_items_parents_before_children(self):
        resolver = self.setup_resolver(items=[
            {'guid': 3, 'parent_guid': 2},
            {'guid': 1337},
            {'guid': 2, 'parent_guid': 1},
            {'guid': 1},
            {'guid': 'qux', 'parent_guid': 1337},
        ])

        self.assertEqual([
            {'guid': 1337},
            {'guid': 'qux', 'parent_guid': 1337},
            {'guid': 1},
            {'guid': 2, 'parent_guid': 1},
            {'guid': 3, 'parent_guid': 2}],
            list(resolver)
        )

    def test_defines_guid_mapping_on_transmogrifier(self):
        item = {'guid': 'marvin'}
        resolver = self.setup_resolver(items=[item])
        transmogrifier = resolver.transmogrifier

        list(resolver)
        self.assertEqual(item, transmogrifier.item_by_guid['marvin'])
