from opengever.bundle.factory import FileNode
from os import utime
from tempfile import mkdtemp
from tempfile import NamedTemporaryFile
from unittest import TestCase
import shutil


class TestFileNode(TestCase):

    def setUp(self):
        super(TestFileNode, self).setUp()
        self.tempdir = mkdtemp()
        self.tempfile = NamedTemporaryFile(dir=self.tempdir, delete=False)
        # set fake access/modification time since epoch
        utime(self.tempfile.name, (1, 83828828))

    def tearDown(self):
        self.tempfile.close()
        shutil.rmtree(self.tempdir)
        super(TestFileNode, self).tearDown()

    def make_node(self, path='/foo', guid='123', parent_guid='456'):
        return FileNode(path, guid, parent_guid)

    def test_truthy_is_document(self):
        self.assertTrue(self.make_node().is_document())

    def test_falsy_is_root(self):
        self.assertFalse(self.make_node().is_root())

    def test_falsy_is_repo(self):
        self.assertFalse(self.make_node().is_repo(0))
        self.assertFalse(self.make_node().is_repo(1))
        self.assertFalse(self.make_node().is_repo(7))

    def test_title(self):
        self.assertEqual('Datii.docx',
                         self.make_node(path='/foo/Business/Datii.docx').title)

    def test_modification_date(self):
        node = self.make_node(path=self.tempfile.name)
        self.assertIsNotNone(node.modification_date)
        self.assertEqual('1972-08-28T06:47:08', node.modification_date)

    def test_creation_date(self):
        node = self.make_node(path=self.tempfile.name)
        # instead of entering the cration date world of pain we just test that
        # it is not None
        self.assertIsNotNone(node.creation_date)
