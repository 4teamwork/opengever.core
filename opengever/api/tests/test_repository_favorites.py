from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import restapi
from opengever.base.model.favorite import Favorite
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID


class TestRepositoryFavorites(IntegrationTestCase):

    @staticmethod
    def uuid(obj):
        return IUUID(obj, None)


class TestRepositoryFavoritesGet(IntegrationTestCase):

    @restapi
    def test_returns_list_of_uids(self, api_client):
        self.login(self.regular_user, api_client)

        favorite1 = create(Builder('favorite')
                           .for_user(self.regular_user)
                           .for_object(self.branch_repofolder))

        favorite2 = create(Builder('favorite')
                           .for_user(self.regular_user)
                           .for_object(self.leaf_repofolder))

        endpoint = '@repository-favorites/{}'.format(self.regular_user.getId())
        api_client.open(endpoint=endpoint)

        self.assertEqual(200, api_client.status_code)
        self.assertEqual([favorite1.plone_uid, favorite2.plone_uid], api_client.contents)

    @restapi
    def test_list_only_favorites_for_given_user(self, api_client):
        self.login(self.regular_user, api_client)

        favorite1 = create(Builder('favorite')
                           .for_user(self.regular_user)
                           .for_object(self.branch_repofolder))

        create(Builder('favorite')
               .for_user(self.dossier_responsible)
               .for_object(self.leaf_repofolder))

        endpoint = '@repository-favorites/{}'.format(self.regular_user.getId())
        api_client.open(endpoint=endpoint)

        self.assertEqual(200, api_client.status_code)
        self.assertEqual([favorite1.plone_uid], api_client.contents)

    @restapi
    def test_list_only_repositoryfolder_favorites(self, api_client):
        self.login(self.regular_user, api_client)

        favorite1 = create(Builder('favorite')
                           .for_user(self.regular_user)
                           .for_object(self.branch_repofolder))

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier))

        endpoint = '@repository-favorites/{}'.format(self.regular_user.getId())
        api_client.open(endpoint=endpoint)

        self.assertEqual(200, api_client.status_code)
        self.assertEqual([favorite1.plone_uid], api_client.contents)

    @restapi
    def test_list_only_favorites_from_current_admin_unit(self, api_client):
        self.login(self.regular_user, api_client)

        favorite1 = create(Builder('favorite')
                           .for_user(self.regular_user)
                           .for_object(self.branch_repofolder))

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.leaf_repofolder)
               .having(admin_unit_id='sk'))

        endpoint = '@repository-favorites/{}'.format(self.regular_user.getId())
        api_client.open(endpoint=endpoint)

        self.assertEqual(200, api_client.status_code)
        self.assertEqual([favorite1.plone_uid], api_client.contents)

    @restapi
    def test_raises_when_userid_is_missing(self, api_client):
        self.login(self.regular_user, api_client)

        with api_client.expect_http_error(400):
            api_client.open(endpoint='@repository-favorites')

        expected_error = {
            "message": "Must supply exactly one parameter (user id)",
            "type": "BadRequest",
        }
        self.assertEqual(expected_error, api_client.contents)


class TestRepositoryFavoritesPost(TestRepositoryFavorites):

    @restapi
    def test_adding_favorite(self, api_client):
        self.login(self.regular_user, api_client)
        self.assertEqual(0, Favorite.query.count())

        endpoint = '@repository-favorites/{}'.format(self.regular_user.getId())
        api_client.open(endpoint=endpoint, data={'uuid': self.uuid(self.document)})

        self.assertEqual(201, api_client.status_code)
        self.assertEqual(u'http://nohost/plone/@favorites/kathi.barfuss/1', api_client.headers.get('location'))

        api_client.open(api_client.headers.get('location'))
        self.assertEqual(1, Favorite.query.count())

    @restapi
    def test_raises_with_missing_uuid(self, api_client):
        self.login(self.regular_user, api_client)

        with api_client.expect_http_error(400):
            endpoint = '@repository-favorites/{}'.format(self.regular_user.getId())
            api_client.open(endpoint=endpoint, method='POST')

        self.assertEquals({u'message': u'Missing parameter uuid', u'type': u'BadRequest'}, api_client.contents)

    @restapi
    def test_raises_unauthorized_when_accessing_favorites_of_other_user(self, api_client):
        self.login(self.regular_user, api_client)

        with api_client.expect_http_error(401):
            endpoint = '@repository-favorites/{}'.format(self.dossier_responsible.getId())
            api_client.open(endpoint=endpoint, data={'uuid': self.uuid(self.document)})

        expected_error = {u'message': u"It's not allowed to add favorites for other users.", u'type': u'Unauthorized'}
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_adding_already_existing_favorite_returns_409_and_existing_representation(self, api_client):
        self.login(self.administrator, api_client)

        create(Builder('favorite')
               .for_user(self.administrator)
               .for_object(self.document))

        with api_client.expect_http_error(409):
            endpoint = '@repository-favorites/{}'.format(self.administrator.getId())
            api_client.open(endpoint=endpoint, data={'uuid': self.uuid(self.document)})

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


class TestFavoritesDelete(TestRepositoryFavorites):

    @restapi
    def test_raises_when_id_is_missing(self, api_client):
        self.login(self.regular_user, api_client)

        with api_client.expect_http_error(400):
            endpoint = '@repository-favorites/{}'.format(self.regular_user.getId())
            api_client.open(endpoint=endpoint, method='DELETE')

        expected_error = {u'message': u'Must supply exactly two parameters (user id and uuid)', u'type': u'BadRequest'}
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_raises_when_favorite_is_not_owned_by_the_given_user(self, api_client):
        self.login(self.regular_user, api_client)

        favorite = create(Builder('favorite')
                          .for_user(self.dossier_responsible)
                          .for_object(self.dossier))

        self.assertEqual(1, Favorite.query.count())

        with api_client.expect_http_error(404):
            endpoint = '@repository-favorites/{}/{}'.format(self.regular_user.getId(), favorite.favorite_id)
            api_client.open(endpoint=endpoint, method='DELETE')

        expected_error = {
            u"message": u'Resource not found: http://nohost/plone/@repository-favorites/kathi.barfuss/1',
            u"type": u"NotFound",
        }
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_removes_favorite_when_already_exists_for_user(self, api_client):
        self.login(self.regular_user, api_client)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier)
               .having(position=0))

        self.assertEqual(1, Favorite.query.count())

        endpoint = '@repository-favorites/{}/{}'.format(self.regular_user.getId(), self.uuid(self.dossier))
        api_client.open(endpoint=endpoint, method='DELETE')

        self.assertEqual(204, api_client.status_code)
        self.assertEqual(0, Favorite.query.count())

    @restapi
    def test_raises_unauthorized_when_removing_a_favorite_of_a_other_user(self, api_client):
        self.login(self.regular_user, api_client)

        create(Builder('favorite')
               .for_user(self.dossier_responsible)
               .for_object(self.dossier))

        self.assertEqual(1, Favorite.query.count())

        with api_client.expect_http_error(401):
            endpoint = '@favorites/{}/{}'.format(self.dossier_responsible.getId(), self.uuid(self.dossier))
            api_client.open(endpoint=endpoint, method='DELETE')

        expected_error = {u'message': u"It's not allowed to delete favorites of other users.", u'type': u'Unauthorized'}
        self.assertEqual(expected_error, api_client.contents)
