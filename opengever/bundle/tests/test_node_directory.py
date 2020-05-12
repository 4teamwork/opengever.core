from opengever.bundle.factory import DirectoryNode
from unittest import TestCase


class TestDirectoryNode(TestCase):

    def make_node(self, path='/foo', guid='123', parent_guid='456', level=0):
        return DirectoryNode(path, guid, parent_guid, level)

    def test_falsy_is_document(self):
        self.assertFalse(self.make_node().is_document())

    def test_truthy_is_root(self):
        self.assertTrue(self.make_node().is_root())

    def test_falsy_is_root(self):
        self.assertFalse(self.make_node(level=1).is_root())

    def test_truthy_is_repo(self):
        node = self.make_node(level=2)
        self.assertTrue(node.is_repo(2))
        self.assertTrue(node.is_repo(3))
        self.assertTrue(node.is_repo(99))

    def test_falsy_is_repo(self):
        node = self.make_node(level=2)
        self.assertFalse(node.is_repo(0))
        self.assertFalse(node.is_repo(1))

    def test_title(self):
        self.assertEqual('Business',
                         self.make_node(path='/foo/Business').title)
