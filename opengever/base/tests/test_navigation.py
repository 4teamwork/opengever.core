from contextlib import contextmanager
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.uuid.interfaces import IUUID
import json


class TestNavigation(FunctionalTestCase):

    def test_caching_url_changes_when_repository_is_changed(self):
        root = create(Builder('repository_root'))
        view = root.restrictedTraverse('navigation.json')

        msg = 'Cache URL did not change after adding a repository folder.'
        with self.assert_changes(view.get_caching_url, msg):
            folder = create(Builder('repository').within(root))

        msg = 'Cache URL did not change after changing a repository folder.'
        with self.assert_changes(view.get_caching_url, msg):
            folder.reindexObject()  # changes the modified date

    @browsing
    def test_json_is_valid(self, browser):
        root = create(Builder('repository_root'))
        folder = create(Builder('repository')
                        .titled('The Folder')
                        .within(root))
        subfolder = create(Builder('repository')
                           .titled('The Sub Folder')
                           .within(folder))

        browser.login().visit(root, view='navigation.json')
        self.assert_json_equal(
            [{"text": "1. The Folder",
              "uid": IUUID(folder),
              "path": '/'.join(folder.getPhysicalPath()),
              "nodes": [{"text": "1.1. The Sub Folder",
                         "nodes": [],
                         "uid": IUUID(subfolder),
                         "path": '/'.join(subfolder.getPhysicalPath()),
                         }],
              }],
            browser.json)

    @browsing
    def test_caching_headers_are_only_set_with_cache_key(self, browser):
        # We should never cache the navigation.json when there is no
        # cache key parameter which will change. Otherwise we will no
        # longer be able to flush the cache.
        root = create(Builder('repository_root'))

        browser.login().visit(root, view='navigation.json')
        self.assertEquals(None, browser.headers.get('Cache-Control'))

        browser.visit(root, view='navigation.json?cache_key=1')
        self.assertEquals('private, max-age=31536000',
                          browser.headers.get('Cache-Control'))

    @contextmanager
    def assert_changes(self, value_callback, msg=None):
        before = value_callback()
        yield
        after = value_callback()
        self.assertNotEqual(before, after, msg)

    def assert_json_equal(self, expected, got, msg=None):
        pretty = {'sort_keys': True, 'indent': 4, 'separators': (',', ': ')}
        expected_json = json.dumps(expected, **pretty)
        got_json = json.dumps(got, **pretty)
        self.maxDiff = None
        self.assertMultiLineEqual(expected_json, got_json, msg)
