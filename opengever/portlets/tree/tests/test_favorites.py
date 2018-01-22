from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestRepositoryFavorites(IntegrationTestCase):

    def test_managing_favorites(self):
        self.login(self.regular_user)

        favorites = self.get_favorites_for('john.doe')

        self.assertEquals([], favorites.list())
        favorites.add('foo')
        favorites.add('bar')
        self.assertEquals(['foo', 'bar'], favorites.list())

        favorites.remove('foo')
        self.assertEquals(['bar'], favorites.list())

        favorites.set(['foo', 'bar', 'baz'])
        self.assertEquals(['foo', 'bar', 'baz'], favorites.list())

    def test_persistence_per_user(self):
        self.login(self.regular_user)

        self.get_favorites_for('hans').add('foo')
        self.assertEquals(['foo'], self.get_favorites_for('hans').list())

        self.get_favorites_for('peter').add('bar')
        self.assertEquals(['bar'], self.get_favorites_for('peter').list())

        self.assertEquals(['foo'], self.get_favorites_for('hans').list())


class TestRepositoryFavoritesView(IntegrationTestCase):

    @browsing
    def test_managing_favorites(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.repository_root, view='repository-favorites/list')

        self.assertEquals([], browser.json)

        browser.open(
            self.repository_root,
            {'uuid': 'foo'},
            view='repository-favorites/add',
            )

        self.assertEquals(
            ['foo'],
            self.get_favorites_for(self.regular_user.id).list(),
            )

        browser.open(
            self.repository_root,
            {'uuids[]': ['foo', 'bar', 'baz']},
            view='repository-favorites/set',
            )

        browser.open(
            self.repository_root,
            {'uuid': 'bar'},
            view='repository-favorites/remove',
            )

        browser.open(self.repository_root, view='repository-favorites/list')

        self.assertEquals(['foo', 'baz'], browser.json)

    def test_cache_invalidates(self):
        self.login(self.regular_user)

        view = self.repository_root.restrictedTraverse('repository-favorites')
        param = view.list_cache_param()

        self.assertEqual(param, view.list_cache_param())

        self.get_favorites_for(self.regular_user.id).add('foo!')

        self.assertNotEqual(param, view.list_cache_param())
