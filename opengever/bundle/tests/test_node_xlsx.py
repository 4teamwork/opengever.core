from opengever.bundle.xlsx import XLSXNode
from unittest import TestCase


class TestXLSXNode(TestCase):

    def make_node(self, item=None, refnum_to_guid=None):
        if item is None:
            item = {'effective_title': 'Foo'}
        if refnum_to_guid is None:
            refnum_to_guid = {}

        return XLSXNode(item, refnum_to_guid)

    def test_falsy_is_document(self):
        self.assertFalse(self.make_node().is_document())

    def test_truthy_is_root(self):
        self.assertTrue(self.make_node().is_root())

    def test_falsy_is_root_level_1(self):
        level_1_item = {
            'effective_title': 'Foo',
            'reference_number': '1'
        }
        level_1_refnum_to_guid = {
            None: 'foo'
        }
        node = self.make_node(item=level_1_item,
                              refnum_to_guid=level_1_refnum_to_guid)
        self.assertFalse(node.is_root())

    def test_falsy_is_root_level_2(self):
        level_2_item = {
            'effective_title': 'Foo',
            'reference_number': '1.0'
        }
        level_2_refnum_to_guid = {
            '1': 'foo'
        }
        node = self.make_node(item=level_2_item,
                              refnum_to_guid=level_2_refnum_to_guid)
        self.assertFalse(node.is_root())

    def test_truthy_is_repo(self):
        self.assertTrue(self.make_node().is_repo(0))
        self.assertTrue(self.make_node().is_repo(1))
        self.assertTrue(self.make_node().is_repo(42))

    def test_title(self):
        self.assertEqual('Foo', self.make_node().title)
