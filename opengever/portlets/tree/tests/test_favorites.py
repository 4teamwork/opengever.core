from opengever.base.favorite import FavoriteManager
from opengever.portlets.tree.interfaces import IRepositoryFavorites
from opengever.testing import IntegrationTestCase
from plone.app.caching.interfaces import IETagValue
from plone.app.testing import logout
from zope.component import getMultiAdapter


class TestRepositoryFavoritesETagValue(IntegrationTestCase):
    def test_etag_is_eqaul_if_nothing_changed(self):
        self.login(self.regular_user)

        value = self.get_etag_value_for(self.portal)
        self.assertEqual(value, self.get_etag_value_for(self.portal))

    def test_etag_value_invalidates_on_add_favorite(self):
        self.login(self.regular_user)

        value = self.get_etag_value_for(self.portal)
        FavoriteManager().add(self.regular_user.getId(), self.branch_repofolder)

        self.assertNotEqual(value, self.get_etag_value_for(self.portal))

    def test_etag_value_invalidates_on_delete_favorite(self):
        self.login(self.regular_user)

        userid = self.regular_user.getId()
        favorite = FavoriteManager().add(userid, self.branch_repofolder)
        value = self.get_etag_value_for(self.portal)
        FavoriteManager().delete(userid, favorite.favorite_id)

        self.assertNotEqual(value, self.get_etag_value_for(self.portal))

    def test_etag_value_for_anonymous(self):
        logout()
        self.assertEquals('', self.get_etag_value_for(self.portal))

    def favorites_for(self, username):
        return getMultiAdapter((self.root, username), IRepositoryFavorites)

    def get_etag_value_for(self, context):
        adapter = getMultiAdapter((context, self.request),
                                  IETagValue,
                                  name='repository-favorites')
        return adapter()
