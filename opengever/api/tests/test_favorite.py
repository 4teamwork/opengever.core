from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase
import json


class TestFavoritesGET(IntegrationTestCase):

    @browsing
    def test_list_all_favorites_for_the_given_userid(self, browser):
        self.login(self.administrator, browser=browser)

        create(Builder('favorite')
               .for_user(self.administrator)
               .for_object(self.dossier))

        create(Builder('favorite')
               .for_user(self.administrator)
               .for_object(self.document))

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.empty_dossier))

        url = '{}/@favorites/{}'.format(self.portal.absolute_url(), self.administrator.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertTrue(
            [{u'@id': 1,
              u'position': 1,
              u'oguid': u'plone:1014013300',
              u'url': u'http://nohost/plone/resolve_oguid/plone:1014013300',
              u'tooltip_url': None,
              u'icon_class': u'contenttype-opengever-dossier-businesscasedossier',
              u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'},
             {u'@id': 2,
              u'position': 2,
              u'oguid': u'plone:1014073300',
              u'url': u'http://nohost/plone/resolve_oguid/plone:1014073300',
              u'tooltip_url': u'http://nohost/plone/resolve_oguid/plone:1014073300/tooltip',
              u'icon_class': u'icon-docx',
              u'title': u'Vertr\xe4gsentwurf'}],
            browser.json)

    @browsing
    def test_raises_when_userid_is_missing(self, browser):
        self.login(self.administrator, browser=browser)

        with browser.expect_http_error(500):
            url = '{}/@favorites'.format(self.portal.absolute_url())
            browser.open(url, method='GET',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {"message": "Must supply exactly one parameter (user id)",
             "type": "Exception"},
            browser.json)


class TestFavoritesPost(IntegrationTestCase):

    @browsing
    def test_adding_favorite(self, browser):
        self.login(self.administrator, browser=browser)

        oguid = Oguid.for_object(self.document)
        url = '{}/@favorites/{}'.format(
            self.portal.absolute_url(), self.administrator.getId())

        data = json.dumps({'oguid': oguid.id})
        browser.open(url, data=data, method='POST',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertTrue(
            {u'@id': None,
             u'oguid': u'plone:1014073300',
              u'position': 1,
             u'url': u'http://nohost/plone/resolve_oguid/plone:1014073300',
             u'icon_class': u'icon-docx',
             u'title': u'Vertr\xe4gsentwurf'}, browser.json)

        self.assertEqual(1, Favorite.query.count())
        fav = Favorite.query.first()
        self.assertEquals(self.administrator.getId(), fav.userid)
        self.assertEquals(oguid, fav.oguid)

    @browsing
    def test_raises_with_missing_oguid(self, browser):
        self.login(self.administrator, browser=browser)

        url = '{}/@favorites/{}'.format(
            self.portal.absolute_url(), self.administrator.getId())

        with browser.expect_http_error(500):
            browser.open(url, method='POST', data="{}",
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json'})

        self.assertEquals(
            {u'message': u'Missing parameter oguid', u'type': u'Exception'},
            browser.json)


class TestFavoritesDelete(IntegrationTestCase):

    @browsing
    def test_raises_when_id_is_missing(self, browser):
        self.login(self.administrator, browser=browser)

        create(Builder('favorite')
               .for_user(self.administrator)
               .for_object(self.dossier))

        self.assertEqual(1, Favorite.query.count())

        with browser.expect_http_error(500):
            url = '{}/@favorites/{}'.format(
                self.portal.absolute_url(), self.administrator.getId())
            browser.open(url, method='DELETE',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'message': u'Must supply exactly two parameter (user id and favorite id)',
             u'type': u'Exception'}, browser.json)

    @browsing
    def test_raises_when_favorite_is_not_owned_by_the_given_user(self, browser):
        self.login(self.administrator, browser=browser)

        favorite = create(Builder('favorite')
                          .for_user(self.regular_user)
                          .for_object(self.dossier))

        self.assertEqual(1, Favorite.query.count())

        with browser.expect_http_error(500):
            url = '{}/@favorites/{}/{}'.format(
                self.portal.absolute_url(),
                self.administrator.getId(),
                favorite.favorite_id)

            browser.open(url, method='DELETE',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {u"message": u"Parameter missmatch: Favorite 1 is not owned by nicole.kohler",
             u"type": u"Exception"}, browser.json)

    @browsing
    def test_removes_favorite_when_already_exists_for_user(self, browser):
        self.login(self.administrator, browser=browser)

        favorite = create(Builder('favorite')
                          .for_user(self.administrator)
                          .for_object(self.dossier))

        self.assertEqual(1, Favorite.query.count())

        url = '{}/@favorites/{}/{}'.format(
            self.portal.absolute_url(), self.administrator.getId(),
            favorite.favorite_id)
        browser.open(url, method='DELETE', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertTrue({'added': False}, browser.contents)
        self.assertEqual(0, Favorite.query.count())


class TestFavoritesPatch(IntegrationTestCase):

    @browsing
    def test_raises_when_id_is_missing(self, browser):
        self.login(self.administrator, browser=browser)

        create(Builder('favorite')
               .for_user(self.administrator)
               .for_object(self.dossier))

        with browser.expect_http_error(500):
            url = '{}/@favorites/{}'.format(
                self.portal.absolute_url(), self.administrator.getId())

            browser.open(url, method='PATCH',
                         data=json.dumps({"title": "GEVER Weeklies"}),
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json'})

        self.assertEqual(
            {u'message': u'Must supply exactly two parameter (user id and favorite id)',
             u'type': u'Exception'}, browser.json)

    @browsing
    def test_raises_when_favorite_is_not_owned_by_the_given_user(self, browser):
        self.login(self.administrator, browser=browser)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier))
        favorite = Favorite.query.one()

        with browser.expect_http_error(500):
            url = '{}/@favorites/{}/{}'.format(
                self.portal.absolute_url(),
                self.administrator.getId(),
                favorite.favorite_id)

            browser.open(url, method='PATCH',
                         data=json.dumps({"title": "GEVER Weeklies"}),
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json'})

        self.assertEqual(
            {u"message": u"Parameter missmatch: Favorite 1 is not owned by nicole.kohler",
             u"type": u"Exception"}, browser.json)

    @browsing
    def test_rename_favorite_title(self, browser):
        self.login(self.administrator, browser=browser)

        create(Builder('favorite')
               .for_user(self.administrator)
               .for_object(self.dossier))

        favorite = Favorite.query.one()

        url = '{}/@favorites/{}/{}'.format(
            self.portal.absolute_url(), self.administrator.getId(),
            favorite.favorite_id)

        browser.open(url, method='PATCH',
                     data=json.dumps({'title': u'\xdcbersicht OGIPs'}),
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'\xdcbersicht OGIPs', favorite.title)
        self.assertTrue(favorite.is_title_personalized)

    @browsing
    def test_update_position(self, browser):
        self.login(self.administrator, browser=browser)

        create(Builder('favorite')
               .for_user(self.administrator)
               .for_object(self.dossier))

        favorite = Favorite.query.one()

        url = '{}/@favorites/{}/{}'.format(
            self.portal.absolute_url(), self.administrator.getId(),
            favorite.favorite_id)

        browser.open(url, method='PATCH',
                     data=json.dumps({'position': 31}),
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEqual(31, favorite.position)
        self.assertEqual(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung', favorite.title)
        self.assertFalse(favorite.is_title_personalized)
