from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.model.favorite import Favorite
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID
import json


class TestRepositoryFavoritesGet(IntegrationTestCase):

    @browsing
    def test_returns_list_of_uids(self, browser):
        self.login(self.regular_user, browser=browser)

        favorite1 = create(Builder('favorite')
                           .for_user(self.regular_user)
                           .for_object(self.branch_repofolder))

        favorite2 = create(Builder('favorite')
                           .for_user(self.regular_user)
                           .for_object(self.leaf_repofolder))

        url = '{}/@repository-favorites/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEqual([favorite1.plone_uid, favorite2.plone_uid],
                         browser.json)

    @browsing
    def test_list_only_favorites_for_given_user(self, browser):
        self.login(self.regular_user, browser=browser)

        favorite1 = create(Builder('favorite')
                           .for_user(self.regular_user)
                           .for_object(self.branch_repofolder))

        create(Builder('favorite')
               .for_user(self.dossier_responsible)
               .for_object(self.leaf_repofolder))

        url = '{}/@repository-favorites/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEqual([favorite1.plone_uid], browser.json)

    @browsing
    def test_list_only_repositoryfolder_favorites(self, browser):
        self.login(self.regular_user, browser=browser)

        favorite1 = create(Builder('favorite')
                           .for_user(self.regular_user)
                           .for_object(self.branch_repofolder))

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier))

        url = '{}/@repository-favorites/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEqual([favorite1.plone_uid], browser.json)

    @browsing
    def test_list_only_favorites_from_current_admin_unit(self, browser):
        self.login(self.regular_user, browser=browser)

        favorite1 = create(Builder('favorite')
                           .for_user(self.regular_user)
                           .for_object(self.branch_repofolder))

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.leaf_repofolder)
               .having(admin_unit_id='sk'))

        url = '{}/@repository-favorites/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEqual([favorite1.plone_uid], browser.json)

    @browsing
    def test_raises_when_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            url = '{}/@repository-favorites'.format(self.portal.absolute_url())
            browser.open(url, method='GET',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {"message": "Must supply exactly one parameter (user id)",
             "type": "BadRequest"},
            browser.json)


class TestRepositoryFavoritesPost(IntegrationTestCase):

    def uuid(self, obj):
        return IUUID(obj, None)

    @browsing
    def test_adding_favorite(self, browser):
        self.login(self.regular_user, browser=browser)

        uuid = self.uuid(self.document)

        url = '{}/@repository-favorites/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId())

        self.assertEqual(0, Favorite.query.count())

        data = json.dumps({'uuid': uuid})
        browser.open(url, data=data, method='POST',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEqual(201, browser.status_code)

        self.assertEqual(u'http://nohost/plone/@favorites/kathi.barfuss/1',
                         browser.headers.get('location'))

        browser.open(browser.headers.get('location'), method='GET',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEqual(1, Favorite.query.count())

    @browsing
    def test_raises_with_missing_uuid(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@repository-favorites/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId())

        with browser.expect_http_error(400):
            browser.open(url, method='POST', data="{}",
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json'})

        self.assertEquals(
            {u'message': u'Missing parameter uuid', u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_raises_unauthorized_when_accessing_favorites_of_other_user(self, browser):
        self.login(self.regular_user, browser=browser)

        uuid = self.uuid(self.document)
        url = '{}/@repository-favorites/{}'.format(
            self.portal.absolute_url(), self.dossier_responsible.getId())

        data = json.dumps({'uuid': uuid})
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

        uuid = self.uuid(self.document)
        url = '{}/@repository-favorites/{}'.format(
            self.portal.absolute_url(), self.administrator.getId())
        data = json.dumps({'uuid': uuid})

        with browser.expect_http_error(409):
            browser.open(url, data=data, method='POST',
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json'})

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@favorites/nicole.kohler/1',
             u'admin_unit': u'Hauptmandant',
             u'favorite_id': 1,
             u'icon_class': u'icon-docx',
             u'oguid': u'plone:1014073300',
             u'uid': IUUID(self.document),
             u'portal_type': u'opengever.document.document',
             u'position': None,
             u'target_url': u'http://nohost/plone/resolve_oguid/plone:1014073300',
             u'title': u'Vertr\xe4gsentwurf',
             u'tooltip_url': u'http://nohost/plone/resolve_oguid/plone:1014073300/tooltip'},
            browser.json)

        self.assertEqual(1, Favorite.query.count())


class TestFavoritesDelete(IntegrationTestCase):

    def uuid(self, obj):
        return IUUID(obj, None)

    @browsing
    def test_raises_when_id_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            url = '{}/@repository-favorites/{}'.format(
                self.portal.absolute_url(), self.regular_user.getId())
            browser.open(url, method='DELETE',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'message': u'Must supply exactly two parameters (user id and uuid)',
             u'type': u'BadRequest'}, browser.json)

    @browsing
    def test_raises_when_favorite_is_not_owned_by_the_given_user(self, browser):
        self.login(self.regular_user, browser=browser)

        favorite = create(Builder('favorite')
                          .for_user(self.dossier_responsible)
                          .for_object(self.dossier))

        self.assertEqual(1, Favorite.query.count())

        with browser.expect_http_error(404):
            url = '{}/@repository-favorites/{}/{}'.format(
                self.portal.absolute_url(),
                self.regular_user.getId(),
                favorite.favorite_id)

            browser.open(url, method='DELETE',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {u"message": u'Resource not found: http://nohost/plone/@repository-favorites/kathi.barfuss/1',
             u"type": u"NotFound"}, browser.json)

    @browsing
    def test_removes_favorite_when_already_exists_for_user(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier)
               .having(position=0))

        self.assertEqual(1, Favorite.query.count())

        url = '{}/@repository-favorites/{}/{}'.format(
            self.portal.absolute_url(), self.regular_user.getId(),
            self.uuid(self.dossier))
        browser.open(url, method='DELETE', headers={'Accept': 'application/json'})

        self.assertEqual(204, browser.status_code)
        self.assertEqual(0, Favorite.query.count())

    @browsing
    def test_raises_unauthorized_when_removing_a_favorite_of_a_other_user(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('favorite')
               .for_user(self.dossier_responsible)
               .for_object(self.dossier))

        self.assertEqual(1, Favorite.query.count())

        url = '{}/@favorites/{}/{}'.format(
            self.portal.absolute_url(), self.dossier_responsible.getId(),
            self.uuid(self.dossier))

        with browser.expect_http_error(401):
            browser.open(url, method='DELETE', headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'message': u"It's not allowed to delete favorites of other users.",
             u'type': u'Unauthorized'},
            browser.json)
