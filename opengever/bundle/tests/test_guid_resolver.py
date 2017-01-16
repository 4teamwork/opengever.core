from opengever.bundle.exceptions import DuplicateGUID
from opengever.bundle.exceptions import MissingGUID
from opengever.bundle.exceptions import MissingParent
from opengever.bundle.loader import GUIDResolver
from unittest2 import TestCase


class TestGUIDResolver(TestCase):

    def setup_resolver(self, items):
        resolver = GUIDResolver(items)
        return resolver

    def test_requires_guid(self):
        with self.assertRaises(MissingGUID):
            self.setup_resolver(items=[{'foo': 1234}])

    def test_prevents_duplicate_guid(self):
        with self.assertRaises(DuplicateGUID):
            self.setup_resolver(items=[{'guid': 1234}, {'guid': 1234}])

    def test_validates_parent_guid(self):
        with self.assertRaises(MissingParent):
            self.setup_resolver(items=[{'guid': 1234, 'parent_guid': 1337}])

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

    def test_builds_guid_mapping(self):
        item = {'guid': 'marvin'}
        resolver = self.setup_resolver(items=[item])
        self.assertEqual(item, resolver.item_by_guid['marvin'])
