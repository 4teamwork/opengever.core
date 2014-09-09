from contextlib import contextmanager
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


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
        create(Builder('repository').within(root).titled('The Folder'))
        browser.login().visit(root, view='navigation.json')
        self.assertEqual('0 The Folder', browser.json[0]['text'])

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
