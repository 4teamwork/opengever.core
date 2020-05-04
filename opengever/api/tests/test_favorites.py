from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID
import json


class TestFavoritesGet(IntegrationTestCase):

    @browsing
    def test_list_all_favorites_for_the_given_userid(self, browser):
        self.login(self.regular_user, browser=browser)

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

        url = '{}/@favorites/{}'.format(self.portal.absolute_url(),
                                        self.regular_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.maxDiff = None
        self.assertEquals(
            [{u'@id': u'http://nohost/plone/@favorites/kathi.barfuss/1',
              u'uid': IUUID(self.dossier),
              u'portal_type': u'opengever.dossier.businesscasedossier',
              u'favorite_id': 1,
              u'is_leafnode': None,
              u'is_subdossier': False,
              u'oguid': u'plone:1014013300',
              u'admin_unit': u'Hauptmandant',
              u'position': 23,
              u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014013300',
              u'tooltip_url': None,
              u'review_state': u'dossier-state-active',
              u'icon_class': u'contenttype-opengever-dossier-businesscasedossier',
              u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'},
             {u'@id': u'http://nohost/plone/@favorites/kathi.barfuss/2',
              u'uid': IUUID(self.document),
              u'portal_type': u'opengever.document.document',
              u'favorite_id': 2,
              u'is_leafnode': None,
              u'is_subdossier': None,
              u'review_state': u'document-state-draft',
              u'position': 21,
              u'oguid': u'plone:1014073300',
              u'admin_unit': u'Hauptmandant',
              u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014073300',
              u'tooltip_url': u'http://nohost/plone/resolve_oguid/plone:1014073300/tooltip',
              u'icon_class': u'icon-docx',
              u'title': u'Vertr\xe4gsentwurf'}],
            browser.json)

    @browsing
    def test_returns_serialized_favorites_for_the_given_userid_and_favorite_id(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier)
               .having(position=23))

        url = '{}/@favorites/{}/1'.format(
            self.portal.absolute_url(), self.regular_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEquals(
            {u'@id': u'http://nohost/plone/@favorites/kathi.barfuss/1',
             u'uid': IUUID(self.dossier),
             u'portal_type': u'opengever.dossier.businesscasedossier',
             u'favorite_id': 1,
             u'is_leafnode': None,
             u'is_subdossier': False,
             u'review_state': u'dossier-state-active',
             u'position': 23,
             u'oguid': u'plone:1014013300',
             u'admin_unit': u'Hauptmandant',
             u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014013300',
             u'tooltip_url': None,
             u'icon_class': u'contenttype-opengever-dossier-businesscasedossier',
             u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'},
            browser.json)

    @browsing
    def test_raises_when_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            url = '{}/@favorites'.format(self.portal.absolute_url())
            browser.open(url, method='GET',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {"message": "Must supply user ID as URL and optional the "
             "favorite id as path parameter.",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_raises_unauthorized_when_accessing_favorites_of_other_user(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(401):
            url = '{}/@favorites/{}'.format(
                self.portal.absolute_url(), self.dossier_responsible.getId())
            browser.open(url, method='GET',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'message': u"It's not allowed to access favorites of other users.",
             u'type': u'Unauthorized'},
            browser.json)


class TestFavoritesPost(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_adding_favorite_by_oguid(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        oguid = Oguid.for_object(self.document)
        url = '{}/@favorites/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId())

        data = json.dumps({'oguid': oguid.id})
        browser.open(url, data=data, method='POST',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEqual(201, browser.status_code)

        self.assertEqual(u'http://nohost/plone/@favorites/kathi.barfuss/1',
                         browser.headers.get('location'))

        browser.open(browser.headers.get('location'), method='GET',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEquals(
            {u'@id': u'http://nohost/plone/@favorites/kathi.barfuss/1',
             u'uid': IUUID(self.document),
             u'portal_type': u'opengever.document.document',
             u'favorite_id': 1,
             u'oguid': u'plone:1014073300',
             u'position': 0,
             u'review_state': u'document-state-draft',
             u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014073300',
             u'tooltip_url': u'http://nohost/plone/resolve_oguid/plone:1014073300/tooltip',
             u'icon_class': u'icon-docx',
             u'is_leafnode': None,
             u'is_subdossier': None,
             u'admin_unit': u'Hauptmandant',
             u'title': u'Vertr\xe4gsentwurf'}, browser.json)

        self.assertEqual(1, Favorite.query.count())
        fav = Favorite.query.first()
        self.assertEquals(self.regular_user.getId(), fav.userid)
        self.assertEquals(oguid, fav.oguid)

    @browsing
    def test_adding_favorite_by_uid(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        url = '{}/@favorites/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId())
        data = json.dumps({'uid': IUUID(self.document)})
        browser.open(url, data=data, method='POST',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEqual(201, browser.status_code)
        self.assertEqual(u'http://nohost/plone/@favorites/kathi.barfuss/1',
                         browser.headers.get('location'))

        browser.open(browser.headers.get('location'), method='GET',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})
        self.assertEquals(
            {u'@id': u'http://nohost/plone/@favorites/kathi.barfuss/1',
             u'uid': IUUID(self.document),
             u'portal_type': u'opengever.document.document',
             u'favorite_id': 1,
             u'is_leafnode': None,
             u'is_subdossier': None,
             u'review_state': u'document-state-draft',
             u'oguid': Oguid.for_object(self.document),
             u'position': 0,
             u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014073300',
             u'tooltip_url': u'http://nohost/plone/resolve_oguid/plone:1014073300/tooltip',
             u'icon_class': u'icon-docx',
             u'admin_unit': u'Hauptmandant',
             u'title': u'Vertr\xe4gsentwurf'}, browser.json)

        self.assertEqual(1, Favorite.query.count())
        fav = Favorite.query.first()
        self.assertEquals(self.regular_user.getId(), fav.userid)
        self.assertEquals(Oguid.for_object(self.document), fav.oguid)

    @browsing
    def test_raises_with_missing_oguid(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@favorites/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId())

        with browser.expect_http_error(400):
            browser.open(url, method='POST', data="{}",
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json'})

        self.assertEquals(
            {u'message': u'Missing parameter oguid or uid', u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_raises_unauthorized_when_accessing_favorites_of_other_user(self, browser):
        self.login(self.regular_user, browser=browser)

        oguid = Oguid.for_object(self.document)
        url = '{}/@favorites/{}'.format(
            self.portal.absolute_url(), self.dossier_responsible.getId())

        data = json.dumps({'oguid': oguid.id})
        with browser.expect_http_error(401):
            browser.open(url, data=data, method='POST',
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json'})

        self.assertEqual(
            {u'message': u"It's not allowed to add favorites for other users.",
             u'type': u'Unauthorized'},
            browser.json)

    @browsing
    def test_adding_already_existing_favorite_returns_409_and_existing_representation(self, browser):
        self.login(self.administrator, browser=browser)

        create(Builder('favorite')
               .for_user(self.administrator)
               .for_object(self.document))

        oguid = Oguid.for_object(self.document)
        url = '{}/@favorites/{}'.format(
            self.portal.absolute_url(), self.administrator.getId())
        data = json.dumps({'oguid': oguid.id})

        with browser.expect_http_error(409):
            browser.open(url, data=data, method='POST',
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json'})

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@favorites/nicole.kohler/1',
             u'uid': IUUID(self.document),
             u'portal_type': u'opengever.document.document',
             u'admin_unit': u'Hauptmandant',
             u'favorite_id': 1,
             u'is_leafnode': None,
             u'is_subdossier': None,
             u'review_state': u'document-state-draft',
             u'icon_class': u'icon-docx',
             u'oguid': u'plone:1014073300',
             u'position': 0,
             u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014073300',
             u'title': u'Vertr\xe4gsentwurf',
             u'tooltip_url': u'http://nohost/plone/resolve_oguid/plone:1014073300/tooltip'},
            browser.json)

        self.assertEqual(1, Favorite.query.count())


class TestFavoritesDelete(IntegrationTestCase):

    @browsing
    def test_raises_when_id_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier))

        self.assertEqual(1, Favorite.query.count())

        with browser.expect_http_error(400):
            url = '{}/@favorites/{}'.format(
                self.portal.absolute_url(), self.regular_user.getId())
            browser.open(url, method='DELETE',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'message': u'Must supply exactly two parameters (user id and favorite id)',
             u'type': u'BadRequest'}, browser.json)

    @browsing
    def test_raises_when_favorite_is_not_owned_by_the_given_user(self, browser):
        self.login(self.regular_user, browser=browser)

        favorite = create(Builder('favorite')
                          .for_user(self.dossier_responsible)
                          .for_object(self.dossier))

        self.assertEqual(1, Favorite.query.count())

        with browser.expect_http_error(404):
            url = '{}/@favorites/{}/{}'.format(
                self.portal.absolute_url(),
                self.regular_user.getId(),
                favorite.favorite_id)

            browser.open(url, method='DELETE',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {u"message": u'Resource not found: http://nohost/plone/@favorites/kathi.barfuss/1',
             u"type": u"NotFound"}, browser.json)

    @browsing
    def test_removes_favorite_when_already_exists_for_user(self, browser):
        self.login(self.regular_user, browser=browser)

        favorite = create(Builder('favorite')
                          .for_user(self.regular_user)
                          .for_object(self.dossier)
                          .having(position=0))

        self.assertEqual(1, Favorite.query.count())

        url = '{}/@favorites/{}/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId(),
            favorite.favorite_id)
        browser.open(url, method='DELETE', headers={'Accept': 'application/json'})

        self.assertEqual(204, browser.status_code)
        self.assertEqual(0, Favorite.query.count())

    @browsing
    def test_updates_positions_when_deleting_favorite(self, browser):
        self.login(self.administrator, browser=browser)

        fav_on_2 = create(Builder('favorite')
                      .for_user(self.administrator)
                      .having(position=2)
                      .for_object(self.dossier))
        fav_on_0 = create(Builder('favorite')
                      .for_user(self.administrator)
                      .having(position=0)
                      .for_object(self.document))
        fav_on_1 = create(Builder('favorite')
                      .for_user(self.administrator)
                      .having(position=1)
                      .for_object(self.leaf_repofolder))
        fav_on_3 = create(Builder('favorite')
                      .for_user(self.administrator)
                      .having(position=3)
                      .for_object(self.meeting_dossier))

        url = '{}/@favorites/{}/{}'.format(
            self.portal.absolute_url(), self.administrator.getId(),
            fav_on_0.favorite_id)
        browser.open(url, method='DELETE', headers={'Accept': 'application/json'})

        self.assertEqual(0, fav_on_1.position)
        self.assertEqual(1, fav_on_2.position)
        self.assertEqual(2, fav_on_3.position)

    @browsing
    def test_raises_unauthorized_when_removing_a_favorite_of_a_other_user(self, browser):
        self.login(self.regular_user, browser=browser)

        favorite = create(Builder('favorite')
                          .for_user(self.dossier_responsible)
                          .for_object(self.dossier))

        self.assertEqual(1, Favorite.query.count())

        url = '{}/@favorites/{}/{}'.format(
            self.portal.absolute_url(), self.dossier_responsible.getId(),
            favorite.favorite_id)

        with browser.expect_http_error(401):
            browser.open(url, method='DELETE', headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'message': u"It's not allowed to delete favorites of other users.",
             u'type': u'Unauthorized'},
            browser.json)


class TestFavoritesPatch(IntegrationTestCase):

    @browsing
    def test_raises_when_id_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier))

        with browser.expect_http_error(400):
            url = '{}/@favorites/{}'.format(
                self.portal.absolute_url(), self.regular_user.getId())

            browser.open(url, method='PATCH',
                         data=json.dumps({"title": "GEVER Weeklies"}),
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json'})

        self.assertEqual(
            {u'message': u'Must supply user ID and favorite ID as URL path parameters.',
             u'type': u'BadRequest'}, browser.json)

    @browsing
    def test_raises_when_favorite_is_not_owned_by_the_given_user(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('favorite')
               .for_user(self.dossier_responsible)
               .for_object(self.dossier))
        favorite = Favorite.query.one()

        with browser.expect_http_error(404):
            url = '{}/@favorites/{}/{}'.format(
                self.portal.absolute_url(),
                self.regular_user.getId(),
                favorite.favorite_id)

            browser.open(url, method='PATCH',
                         data=json.dumps({"title": "GEVER Weeklies"}),
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json'})

        self.assertEqual(
            {u"message": u'Resource not found: http://nohost/plone/@favorites/kathi.barfuss/1',
             u"type": u"NotFound"}, browser.json)

    @browsing
    def test_raises_unauthorized_when_updating_favorite_of_a_other_user(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('favorite')
               .for_user(self.dossier_responsible)
               .for_object(self.dossier))

        favorite = Favorite.query.one()

        url = '{}/@favorites/{}/{}'.format(
            self.portal.absolute_url(), self.dossier_responsible.getId(),
            favorite.favorite_id)

        with browser.expect_http_error(401):
            browser.open(url, method='PATCH',
                         data=json.dumps({'title': u'\xdcbersicht OGIPs'}),
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json'})

        self.assertEqual(
            {u'message': u"It's not allowed to update favorites of other users.",
             u'type': u'Unauthorized'},
            browser.json)

    @browsing
    def test_rename_favorite_title(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier))

        favorite = Favorite.query.one()

        url = '{}/@favorites/{}/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId(),
            favorite.favorite_id)

        browser.open(url, method='PATCH',
                     data=json.dumps({'title': u'\xdcbersicht OGIPs'}),
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEqual(204, browser.status_code)
        self.assertEqual(u'\xdcbersicht OGIPs', favorite.title)
        self.assertTrue(favorite.is_title_personalized)

    @browsing
    def test_prefer_header_is_respected_return_representation(self, browser):
        self.maxDiff = None

        self.login(self.regular_user, browser=browser)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier))

        favorite = Favorite.query.one()

        url = '{}/@favorites/{}/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId(),
            favorite.favorite_id)

        browser.open(url, method='PATCH',
                     data=json.dumps({'title': u'\xdcbersicht OGIPs'}),
                     headers={'Accept': 'application/json',
                              'Prefer': 'return=representation',
                              'Content-Type': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            {u'@id': u'http://nohost/plone/@favorites/kathi.barfuss/1',
             u'uid': IUUID(self.dossier),
             u'portal_type': u'opengever.dossier.businesscasedossier',
             u'favorite_id': 1,
             u'is_leafnode': None,
             u'is_subdossier': False,
             u'review_state': u'dossier-state-active',
             u'title': u'\xdcbersicht OGIPs',
             u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014013300',
             u'icon_class': u'contenttype-opengever-dossier-businesscasedossier',
             u'tooltip_url': None,
             u'oguid': u'plone:1014013300',
             u'admin_unit': u'Hauptmandant',
             u'position': 0}, browser.json)

    @browsing
    def test_update_position(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier)
               .having(position=0))

        favorite = Favorite.query.one()

        url = '{}/@favorites/{}/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId(),
            favorite.favorite_id)

        browser.open(url, method='PATCH',
                     data=json.dumps({'position': 31}),
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEqual(204, browser.status_code)
        self.assertEqual(31, favorite.position)
        self.assertEqual(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung', favorite.title)
        self.assertFalse(favorite.is_title_personalized)

    @browsing
    def test_update_position_recalculates_positions_move_up(self, browser):
        self.login(self.regular_user, browser=browser)

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

        self.assertEquals(
            [self.dossier, self.document, self.leaf_repofolder,
             self.branch_repofolder],
            [fav.oguid.resolve_object() for fav in
             Favorite.query.order_by(Favorite.position)])

        url = '{}/@favorites/{}/4'.format(
            self.portal.absolute_url(), self.regular_user.getId())
        browser.open(url, method='PATCH',
                     data=json.dumps({'position': 0}),
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEquals(
            [self.branch_repofolder, self.dossier, self.document,
             self.leaf_repofolder],
            [fav.oguid.resolve_object() for fav in Favorite.query.order_by(Favorite.position)])

    @browsing
    def test_update_position_recalculates_positions_move_down(self, browser):
        self.login(self.regular_user, browser=browser)

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

        self.assertEquals(
            [self.dossier, self.document, self.leaf_repofolder,
             self.branch_repofolder],
            [fav.oguid.resolve_object() for fav in
             Favorite.query.order_by(Favorite.position)])

        url = '{}/@favorites/{}/1'.format(
            self.portal.absolute_url(), self.regular_user.getId())
        browser.open(url, method='PATCH',
                     data=json.dumps({'position': 2}),
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEquals(
            [self.document, self.leaf_repofolder, self.dossier, self.branch_repofolder],
            [fav.oguid.resolve_object() for fav in Favorite.query.order_by(Favorite.position)])
