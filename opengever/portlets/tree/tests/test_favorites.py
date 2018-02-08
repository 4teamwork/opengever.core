from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.portlets.tree.interfaces import IRepositoryFavorites
from opengever.testing import FunctionalTestCase
from plone.app.caching.interfaces import IETagValue
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter


class TestRepositoryFavorites(FunctionalTestCase):

    def setUp(self):
        self.root = create(Builder('repository_root'))

    def test_managing_favorites(self):
        favorites = self.favorites_for('john.doe')

        self.assertEquals([], favorites.list())
        favorites.add('foo')
        favorites.add('bar')
        self.assertEquals(['foo', 'bar'], favorites.list())

        favorites.remove('foo')
        self.assertEquals(['bar'], favorites.list())

        favorites.set(['foo', 'bar', 'baz'])
        self.assertEquals(['foo', 'bar', 'baz'], favorites.list())

    def test_persistence_per_user(self):
        self.favorites_for('hans').add('foo')
        self.assertEquals(['foo'], self.favorites_for('hans').list())

        self.favorites_for('peter').add('bar')
        self.assertEquals(['bar'], self.favorites_for('peter').list())

        self.assertEquals(['foo'], self.favorites_for('hans').list())

    def favorites_for(self, username):
        return getMultiAdapter((self.root, username), IRepositoryFavorites)


class TestRepositoryFavoritesView(FunctionalTestCase):

    def setUp(self):
        self.root = create(Builder('repository_root'))
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    @browsing
    def test_managing_favorites(self, browser):
        browser.login()

        browser.open(self.root, view='repository-favorites/list')
        self.assertEquals([], browser.json)

        browser.open(self.root, {'uuid': 'foo'}, view='repository-favorites/add')
        self.assertEquals(['foo'], self.favorites_for(TEST_USER_ID).list())

        browser.open(self.root, {'uuids[]': ['foo', 'bar', 'baz']},
                     view='repository-favorites/set')
        browser.open(self.root, {'uuid': 'bar'}, view='repository-favorites/remove')

        browser.open(self.root, view='repository-favorites/list')
        self.assertEquals(['foo', 'baz'], browser.json)

    def test_cache_invalidates(self):
        view = self.root.restrictedTraverse('repository-favorites')
        param = view.list_cache_param()
        self.assertEqual(param, view.list_cache_param())
        self.favorites_for(TEST_USER_ID).add('foo!')
        self.assertNotEqual(param, view.list_cache_param())

    def test_etag_value_invalidates(self):
        value = self.get_etag_value_for(self.root)
        self.assertEquals(value, self.get_etag_value_for(self.portal))
        self.favorites_for(TEST_USER_ID).add('foo!')
        self.assertNotEqual(value, self.get_etag_value_for(self.root))

    def favorites_for(self, username):
        return getMultiAdapter((self.root, username), IRepositoryFavorites)

    def get_etag_value_for(self, context):
        adapter = getMultiAdapter((context, self.request),
                                  IETagValue,
                                  name='repository-favorites')
        return adapter()
