from contextlib import contextmanager
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestNavigation(IntegrationTestCase):

    def test_caching_url_changes_when_repository_is_changed(self):
        self.login(self.regular_user)
        view = self.repository_root.restrictedTraverse('navigation.json')

        msg = 'Cache URL did not change after adding a repository folder.'
        with self.assert_changes(view.get_caching_url, msg):
            folder = create(Builder('repository').within(self.repository_root))

        msg = 'Cache URL did not change after changing a repository folder.'
        with self.assert_changes(view.get_caching_url, msg):
            folder.reindexObject()  # changes the modified date

    def test_caching_url_contains_current_language_code(self):
        self.login(self.regular_user)

        view = self.repository_root.restrictedTraverse('navigation.json')

        msg = 'Cache URL did not change after changing language.'
        with self.assert_changes(view.get_caching_url, msg):
            self.repository_root.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'fr'

        msg = 'Cache URL did not change after changing language.'
        with self.assert_changes(view.get_caching_url, msg):
            self.repository_root.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'de-ch'

    @browsing
    def test_json_is_valid(self, browser):
        self.login(self.regular_user, browser=browser)

        self.enable_languages()

        browser.open()
        browser.click_on('Deutsch')
        browser.visit(self.repository_root, view='navigation.json')
        expected_tree = [
            {
                u'active': True,
                u'description': u'Alles zum Thema F\xfchrung.',
                u'nodes': [{
                    u'active': True,
                    u'description': u'',
                    u'nodes': [],
                    u'text': u'1.1. Vertr\xe4ge und Vereinbarungen',
                    u'uid': u'createrepositorytree000000000003',
                    u'url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen',
                }],
                u'text': u'1. F\xfchrung',
                u'uid': u'createrepositorytree000000000002',
                u'url': u'http://nohost/plone/ordnungssystem/fuhrung',
            },
            {
                u'active': True,
                u'description': u'',
                u'nodes': [],
                u'text': u'2. Rechnungspr\xfcfungskommission',
                u'uid': u'createrepositorytree000000000004',
                u'url': u'http://nohost/plone/ordnungssystem/rechnungsprufungskommission',
            },
            {
                u'active': False,
                u'description': u'',
                u'nodes': [],
                u'text': u'3. Spinn\xe4nnetzregistrar',
                u'uid': u'createrepositorytree000000000005',
                u'url': u'http://nohost/plone/ordnungssystem/spinnannetzregistrar',
            },
        ]
        self.assertEqual(expected_tree, browser.json)

    @browsing
    def test_caching_headers_are_only_set_with_cache_key(self, browser):
        # We should never cache the navigation.json when there is no
        # cache key parameter which will change. Otherwise we will no
        # longer be able to flush the cache.
        self.login(self.regular_user, browser=browser)

        browser.visit(self.repository_root, view='navigation.json')
        self.assertEquals(None, browser.headers.get('Cache-Control'))

        browser.visit(self.repository_root, view='navigation.json?cache_key=1')
        self.assertEquals('private, max-age=31536000',
                          browser.headers.get('Cache-Control'))

    def test_cachekey_change_precision_is_less_than_minute(self):
        """The precision of the "modified" DateIndex is "minute".

        This means when querying objects and sorting them by modified index
        the sort order may not be correct when objects were changed within the
        same minute.

        We want to make sure that this does not affect the cachekey.
        """
        self.login(self.regular_user)

        with freeze(datetime(2015, 1, 1, 12, 0)) as clock:
            root = create(Builder('repository_root'))
            one = create(Builder('repository').within(root).titled(u'One'))
            two = create(Builder('repository').within(root).titled(u'Two'))
            view = root.restrictedTraverse('navigation.json')

            clock.forward(seconds=1)
            notify(ObjectModifiedEvent(two))
            cachekey_two = view._navigation_cache_key()

            clock.forward(seconds=1)
            notify(ObjectModifiedEvent(one))
            cachekey_one = view._navigation_cache_key()

            self.assertNotEqual(
                cachekey_two, cachekey_one,
                'Cachekey should change when repository is modified.')

    @contextmanager
    def assert_changes(self, value_callback, msg=None):
        before = value_callback()
        yield
        after = value_callback()
        self.assertNotEqual(before, after, msg)
