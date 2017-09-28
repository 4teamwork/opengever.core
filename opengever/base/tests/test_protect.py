from BTrees.OOBTree import OOBTree
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from itertools import chain
from opengever.base.protect import get_buckets_for_btree
from opengever.testing import FunctionalTestCase
import transaction
import unittest


class TestBucketsForBTree(unittest.TestCase):

    def test_get_buckets_for_btree_yield_all_contained_buckets(self):
        tree = OOBTree()
        for i in range(0, 50):
            tree['key-{}'.format(i)] = 'Lorem Ipsum'

        buckets = list(get_buckets_for_btree(tree))
        self.assertEquals(3, len(buckets))

        keys = [bucket.keys() for bucket in buckets]
        self.assertEquals(50, len(list(chain(*keys))))


class TestProtect(FunctionalTestCase):

    def setUp(self):
        super(TestProtect, self).setUp()
        repo_root = create(Builder('repository_root'))
        repo_folder = create(Builder('repository').within(repo_root))
        self.dossier = create(Builder('dossier').within(repo_folder))
        self.document = create(Builder('document').within(self.dossier))

    @browsing
    def test_initializes_annotations_without_csrf_confirmation(self, browser):
        browser.login().open(self.document)
        self.assertEquals(self.document.absolute_url(), browser.url)

        del self.document.__annotations__
        transaction.commit()

        browser.login().open(self.document)
        self.assertEquals(self.document.absolute_url(), browser.url)
