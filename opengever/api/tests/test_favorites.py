from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import restapi
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase


class TestFavoritesGet(IntegrationTestCase):

    @restapi
    def test_list_all_favorites_for_the_given_userid(self, api_client):
        self.login(self.regular_user, api_client)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier)
               .having(position=23))

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.document)
               .having(position=21))

        create(Builder('favorite')
               .for_user(self.dossier_responsible)
               .for_object(self.empty_dossier))

        endpoint = '@favorites/{}'.format(self.regular_user.getId())
        api_client.open(endpoint=endpoint)

        self.assertEqual(200, api_client.status_code)
        expected_user_favorites = [
            {
                u'@id': u'http://nohost/plone/@favorites/kathi.barfuss/1',
                u'favorite_id': 1,
                u'position': 23,
                u'oguid': u'plone:1014013300',
                u'admin_unit': u'Hauptmandant',
                u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014013300',
                u'tooltip_url': None,
                u'icon_class': u'contenttype-opengever-dossier-businesscasedossier',
                u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            },
            {
                u'@id': u'http://nohost/plone/@favorites/kathi.barfuss/2',
                u'favorite_id': 2,
                u'position': 21,
                u'oguid': u'plone:1014073300',
                u'admin_unit': u'Hauptmandant',
                u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014073300',
                u'tooltip_url': u'http://nohost/plone/resolve_oguid/plone:1014073300/tooltip',
                u'icon_class': u'icon-docx',
                u'title': u'Vertr\xe4gsentwurf',
            },
        ]
        self.assertEqual(expected_user_favorites, api_client.contents)

    @restapi
    def test_returns_serialized_favorites_for_the_given_userid_and_favorite_id(self, api_client):
        self.login(self.regular_user, api_client)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier)
               .having(position=23))

        endpoint = '@favorites/{}/1'.format(self.regular_user.getId())
        api_client.open(endpoint=endpoint)

        self.assertEqual(200, api_client.status_code)
        expected_favorite = {
            u'@id': u'http://nohost/plone/@favorites/kathi.barfuss/1',
            u'favorite_id': 1,
            u'position': 23,
            u'oguid': u'plone:1014013300',
            u'admin_unit': u'Hauptmandant',
            u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014013300',
            u'tooltip_url': None,
            u'icon_class': u'contenttype-opengever-dossier-businesscasedossier',
            u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
        }
        self.assertEqual(expected_favorite, api_client.contents)

    @restapi
    def test_raises_when_userid_is_missing(self, api_client):
        self.login(self.regular_user, api_client)

        with api_client.expect_http_error(400):
            api_client.open(endpoint='@favorites')

        expected_error = {
            "message": "Must supply user ID as URL and optional the favorite id as path parameter.",
            "type": "BadRequest",
        }
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_raises_unauthorized_when_accessing_favorites_of_other_user(self, api_client):
        self.login(self.regular_user, api_client)

        with api_client.expect_http_error(401):
            endpoint = '@favorites/{}'.format(self.dossier_responsible.getId())
            api_client.open(endpoint=endpoint)

        expected_error = {u'message': u"It's not allowed to access favorites of other users.", u'type': u'Unauthorized'}
        self.assertEqual(expected_error, api_client.contents)


class TestFavoritesPost(IntegrationTestCase):

    @restapi
    def test_adding_favorite(self, api_client):
        self.login(self.regular_user, api_client)

        oguid = Oguid.for_object(self.document)
        endpoint = '@favorites/{}'.format(self.regular_user.getId())
        data = {'oguid': oguid.id}
        api_client.open(endpoint=endpoint, data=data)
        self.assertEqual(201, api_client.status_code)
        self.assertEqual(u'http://nohost/plone/@favorites/kathi.barfuss/1', api_client.headers.get('location'))

        api_client.open(api_client.headers.get('location'))
        expected_favorite = {
            u'@id': u'http://nohost/plone/@favorites/kathi.barfuss/1',
            u'favorite_id': 1,
            u'oguid': u'plone:1014073300',
            u'position': 0,
            u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014073300',
            u'tooltip_url': u'http://nohost/plone/resolve_oguid/plone:1014073300/tooltip',
            u'icon_class': u'icon-docx',
            u'admin_unit': u'Hauptmandant',
            u'title': u'Vertr\xe4gsentwurf',
        }
        self.assertEqual(expected_favorite, api_client.contents)
        self.assertEqual(1, Favorite.query.count())

        fav = Favorite.query.first()
        self.assertEqual(self.regular_user.getId(), fav.userid)
        self.assertEqual(oguid, fav.oguid)

    @restapi
    def test_raises_with_missing_oguid(self, api_client):
        self.login(self.regular_user, api_client)

        endpoint = '@favorites/{}'.format(self.regular_user.getId())

        with api_client.expect_http_error(400):
            api_client.open(endpoint=endpoint, method='POST')

        expected_error = {u'message': u'Missing parameter oguid', u'type': u'BadRequest'}
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_raises_unauthorized_when_accessing_favorites_of_other_user(self, api_client):
        self.login(self.regular_user, api_client)

        oguid = Oguid.for_object(self.document)
        endpoint = '@favorites/{}'.format(self.dossier_responsible.getId())
        data = {'oguid': oguid.id}
        with api_client.expect_http_error(401):
            api_client.open(endpoint=endpoint, data=data)

        expected_error = {u'message': u"It's not allowed to add favorites for other users.", u'type': u'Unauthorized'}
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_adding_already_existing_favorite_returns_409_and_existing_representation(self, api_client):
        self.login(self.administrator, api_client)

        create(Builder('favorite')
               .for_user(self.administrator)
               .for_object(self.document))

        endpoint = '@favorites/{}'.format(self.administrator.getId())
        oguid = Oguid.for_object(self.document)
        data = {'oguid': oguid.id}

        with api_client.expect_http_error(409):
            api_client.open(endpoint=endpoint, data=data)

        expected_favorite = {
            u'@id': u'http://nohost/plone/@favorites/nicole.kohler/1',
            u'admin_unit': u'Hauptmandant',
            u'favorite_id': 1,
            u'icon_class': u'icon-docx',
            u'oguid': u'plone:1014073300',
            u'position': None,
            u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014073300',
            u'title': u'Vertr\xe4gsentwurf',
            u'tooltip_url': u'http://nohost/plone/resolve_oguid/plone:1014073300/tooltip',
        }
        self.assertEqual(expected_favorite, api_client.contents)
        self.assertEqual(1, Favorite.query.count())


class TestFavoritesDelete(IntegrationTestCase):

    @restapi
    def test_raises_when_id_is_missing(self, api_client):
        self.login(self.regular_user, api_client)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier))

        self.assertEqual(1, Favorite.query.count())

        with api_client.expect_http_error(400):
            endpoint = '@favorites/{}'.format(self.regular_user.getId())
            api_client.open(endpoint=endpoint, method='DELETE')

        expected_error = {
            u'message': u'Must supply exactly two parameters (user id and favorite id)',
            u'type': u'BadRequest',
        }
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_raises_when_favorite_is_not_owned_by_the_given_user(self, api_client):
        self.login(self.regular_user, api_client)

        favorite = create(Builder('favorite')
                          .for_user(self.dossier_responsible)
                          .for_object(self.dossier))

        self.assertEqual(1, Favorite.query.count())

        with api_client.expect_http_error(404):
            endpoint = '@favorites/{}/{}'.format(self.regular_user.getId(), favorite.favorite_id)
            api_client.open(endpoint=endpoint, method='DELETE')

        expected_error = {
            u"message": u'Resource not found: http://nohost/plone/@favorites/kathi.barfuss/1',
            u"type": u"NotFound",
        }
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_removes_favorite_when_already_exists_for_user(self, api_client):
        self.login(self.regular_user, api_client)

        favorite = create(Builder('favorite')
                          .for_user(self.regular_user)
                          .for_object(self.dossier)
                          .having(position=0))

        self.assertEqual(1, Favorite.query.count())

        endpoint = '@favorites/{}/{}'.format(self.regular_user.getId(), favorite.favorite_id)
        api_client.open(endpoint=endpoint, method='DELETE')

        self.assertEqual(204, api_client.status_code)
        self.assertEqual(0, Favorite.query.count())

    @restapi
    def test_updates_positions_when_deleting_favorite(self, api_client):
        self.login(self.administrator, api_client)

        fav1 = create(Builder('favorite')
                      .for_user(self.administrator)
                      .having(position=0)
                      .for_object(self.dossier))
        fav2 = create(Builder('favorite')
                      .for_user(self.administrator)
                      .having(position=1)
                      .for_object(self.document))
        fav3 = create(Builder('favorite')
                      .for_user(self.administrator)
                      .having(position=2)
                      .for_object(self.leaf_repofolder))

        endpoint = '@favorites/{}/{}'.format(self.administrator.getId(), fav1.favorite_id)
        api_client.open(endpoint=endpoint, method='DELETE')

        self.assertEqual(0, fav2.position)
        self.assertEqual(1, fav3.position)

    @restapi
    def test_raises_unauthorized_when_removing_a_favorite_of_a_other_user(self, api_client):
        self.login(self.regular_user, api_client)

        favorite = create(Builder('favorite')
                          .for_user(self.dossier_responsible)
                          .for_object(self.dossier))

        self.assertEqual(1, Favorite.query.count())

        endpoint = '@favorites/{}/{}'.format(self.dossier_responsible.getId(), favorite.favorite_id)

        with api_client.expect_http_error(401):
            api_client.open(endpoint=endpoint, method='DELETE')

        expected_error = {u'message': u"It's not allowed to delete favorites of other users.", u'type': u'Unauthorized'}
        self.assertEqual(expected_error, api_client.contents)


class TestFavoritesPatch(IntegrationTestCase):

    @restapi
    def test_raises_when_id_is_missing(self, api_client):
        self.login(self.regular_user, api_client)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier))

        endpoint = '@favorites/{}'.format(self.regular_user.getId())
        data = {"title": "GEVER Weeklies"}
        with api_client.expect_http_error(400):
            api_client.open(endpoint=endpoint, data=data, method='PATCH')

        expected_error = {
            u'message': u'Must supply user ID and favorite ID as URL path parameters.',
            u'type': u'BadRequest',
        }
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_raises_when_favorite_is_not_owned_by_the_given_user(self, api_client):
        self.login(self.regular_user, api_client)

        create(Builder('favorite')
               .for_user(self.dossier_responsible)
               .for_object(self.dossier))
        favorite = Favorite.query.one()

        endpoint = '@favorites/{}/{}'.format(self.regular_user.getId(), favorite.favorite_id)
        data = {"title": "GEVER Weeklies"}
        with api_client.expect_http_error(404):
            api_client.open(endpoint=endpoint, data=data, method='PATCH')

        expected_error = {
            u"message": u'Resource not found: http://nohost/plone/@favorites/kathi.barfuss/1',
            u"type": u"NotFound",
        }
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_raises_unauthorized_when_updating_favorite_of_a_other_user(self, api_client):
        self.login(self.regular_user, api_client)

        create(Builder('favorite')
               .for_user(self.dossier_responsible)
               .for_object(self.dossier))

        favorite = Favorite.query.one()

        endpoint = '@favorites/{}/{}'.format(self.dossier_responsible.getId(), favorite.favorite_id)
        data = {'title': u'\xdcbersicht OGIPs'}
        with api_client.expect_http_error(401):
            api_client.open(endpoint=endpoint, data=data, method='PATCH')

        expected_error = {u'message': u"It's not allowed to update favorites of other users.", u'type': u'Unauthorized'}
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_rename_favorite_title(self, api_client):
        self.login(self.regular_user, api_client)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier))

        favorite = Favorite.query.one()

        endpoint = '@favorites/{}/{}'.format(self.regular_user.getId(), favorite.favorite_id)
        data = {'title': u'\xdcbersicht OGIPs'}
        api_client.open(endpoint=endpoint, data=data, method='PATCH')

        self.assertEqual(204, api_client.status_code)
        self.assertEqual(u'\xdcbersicht OGIPs', favorite.title)
        self.assertTrue(favorite.is_title_personalized)

    @restapi
    def test_prefer_header_is_respected_return_representation(self, api_client):
        self.login(self.regular_user, api_client)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier))

        favorite = Favorite.query.one()

        endpoint = '@favorites/{}/{}'.format(self.regular_user.getId(), favorite.favorite_id)
        data = {'title': u'\xdcbersicht OGIPs'}
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}
        api_client.open(endpoint=endpoint, headers=headers, data=data, method='PATCH')

        self.assertEqual(200, api_client.status_code)
        expected_favorite = {
            u'@id': u'http://nohost/plone/@favorites/kathi.barfuss/1',
            u'favorite_id': 1,
            u'title': u'\xdcbersicht OGIPs',
            u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014013300',
            u'icon_class': u'contenttype-opengever-dossier-businesscasedossier',
            u'tooltip_url': None,
            u'oguid': u'plone:1014013300',
            u'admin_unit': u'Hauptmandant',
            u'position': None,
        }
        self.assertEqual(expected_favorite, api_client.contents)

    @restapi
    def test_update_position(self, api_client):
        self.login(self.regular_user, api_client)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier)
               .having(position=0))

        favorite = Favorite.query.one()

        endpoint = '@favorites/{}/{}'.format(self.regular_user.getId(), favorite.favorite_id)
        data = {'position': 31}
        api_client.open(endpoint=endpoint, data=data, method='PATCH')

        self.assertEqual(204, api_client.status_code)
        self.assertEqual(31, favorite.position)
        self.assertEqual(u'Vertr\xe4ge mit der kantonalen Finanzverwaltung', favorite.title)
        self.assertFalse(favorite.is_title_personalized)

    @restapi
    def test_update_position_recalculates_positions_move_up(self, api_client):
        self.login(self.regular_user, api_client)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier)
               .having(position=0))

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.document)
               .having(position=1))

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.leaf_repofolder)
               .having(position=2))

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.branch_repofolder)
               .having(position=3))

        self.assertEqual(
            [self.dossier, self.document, self.leaf_repofolder,
             self.branch_repofolder],
            [fav.oguid.resolve_object() for fav in
             Favorite.query.order_by(Favorite.position)])

        endpoint = '@favorites/{}/4'.format(self.regular_user.getId())
        data = {'position': 0}
        api_client.open(endpoint=endpoint, data=data, method='PATCH')

        self.assertEqual(
            [self.branch_repofolder, self.dossier, self.document, self.leaf_repofolder],
            [fav.oguid.resolve_object() for fav in Favorite.query.order_by(Favorite.position)],
        )

    @restapi
    def test_update_position_recalculates_positions_move_down(self, api_client):
        self.login(self.regular_user, api_client)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier)
               .having(position=0, title='Dossier'))

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.document)
               .having(position=1, title='Document'))

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.leaf_repofolder)
               .having(position=2, title='Leaf repofolder'))

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.branch_repofolder)
               .having(position=3, title='Branch repofolder'))

        self.assertEqual(
            [self.dossier, self.document, self.leaf_repofolder, self.branch_repofolder],
            [fav.oguid.resolve_object() for fav in Favorite.query.order_by(Favorite.position)],
        )

        endpoint = '@favorites/{}/1'.format(self.regular_user.getId())
        data = {'position': 2}
        api_client.open(endpoint=endpoint, data=data, method='PATCH')

        self.assertEqual(
            [self.document, self.leaf_repofolder, self.dossier, self.branch_repofolder],
            [fav.oguid.resolve_object() for fav in Favorite.query.order_by(Favorite.position)],
        )
