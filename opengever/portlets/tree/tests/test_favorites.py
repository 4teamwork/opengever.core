from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.portlets.tree.interfaces import IRepositoryFavorites
from opengever.testing import FunctionalTestCase
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

    def favorites_for(self, username):
        return getMultiAdapter((self.root, username), IRepositoryFavorites)
