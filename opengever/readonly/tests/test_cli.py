from contextlib import contextmanager
from opengever.readonly.cli import disable_readonly
from opengever.readonly.cli import enable_readonly
from opengever.readonly.cli import is_readonly
from unittest import TestCase
import filecmp
import os.path
import shutil
import tempfile


data_dir = os.path.join(os.path.dirname(__file__), 'data')


class TestReadOnlyToggle(TestCase):

    def test_is_readonly_returns_true_if_readonly_enabled(self):
        self.assertTrue(
            is_readonly(os.path.join(data_dir, 'filestorage-ro-zope.conf')))
        self.assertTrue(
            is_readonly(os.path.join(data_dir, 'zeoclient-ro-zope.conf')))
        self.assertTrue(
            is_readonly(os.path.join(data_dir, 'relstorage-ro-zope.conf')))

    def test_is_readonly_returns_false_if_readonly_disabled(self):
        self.assertFalse(
            is_readonly(os.path.join(data_dir, 'filestorage-rw-zope.conf')))
        self.assertFalse(
            is_readonly(os.path.join(data_dir, 'zeoclient-rw-zope.conf')))
        self.assertFalse(
            is_readonly(os.path.join(data_dir, 'relstorage-rw-zope.conf')))

    def test_enable_readonly_in_filestorage_zope_conf(self):
        with self.zope_conf('filestorage-rw-zope.conf') as conf:
            enable_readonly(conf)
            expected = os.path.join(data_dir, 'filestorage-ro-zope.conf')
            self.assertTrue(
                filecmp.cmp(conf, expected), 'Unexpected content in zope.conf')

    def test_disable_readonly_in_filestorage_zope_conf(self):
        with self.zope_conf('filestorage-ro-zope.conf') as conf:
            disable_readonly(conf)
            expected = os.path.join(data_dir, 'filestorage-rw-zope.conf')
            self.assertTrue(
                filecmp.cmp(conf, expected), 'Unexpected content in zope.conf')

    def test_enable_readonly_in_zeoclient_zope_conf(self):
        with self.zope_conf('zeoclient-rw-zope.conf') as conf:
            enable_readonly(conf)
            expected = os.path.join(data_dir, 'zeoclient-ro-zope.conf')
            self.assertTrue(
                filecmp.cmp(conf, expected), 'Unexpected content in zope.conf')

    def test_disable_readonly_in_zeoclient_zope_conf(self):
        with self.zope_conf('zeoclient-ro-zope.conf') as conf:
            disable_readonly(conf)
            expected = os.path.join(data_dir, 'zeoclient-rw-zope.conf')
            self.assertTrue(
                filecmp.cmp(conf, expected), 'Unexpected content in zope.conf')

    def test_enable_readonly_in_relstorage_zope_conf(self):
        with self.zope_conf('relstorage-rw-zope.conf') as conf:
            enable_readonly(conf)
            expected = os.path.join(data_dir, 'relstorage-ro-zope.conf')
            self.assertTrue(
                filecmp.cmp(conf, expected), 'Unexpected content in zope.conf')

    def test_disable_readonly_in_relstorage_zope_conf(self):
        with self.zope_conf('relstorage-ro-zope.conf') as conf:
            disable_readonly(conf)
            expected = os.path.join(data_dir, 'relstorage-rw-zope.conf')
            self.assertTrue(
                filecmp.cmp(conf, expected), 'Unexpected content in zope.conf')

    @contextmanager
    def zope_conf(self, name):
        tempdir = tempfile.mkdtemp()
        shutil.copy(os.path.join(data_dir, name), tempdir)
        yield os.path.join(tempdir, name)
        shutil.rmtree(tempdir)
