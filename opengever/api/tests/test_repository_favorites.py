from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestRepositoryFavoritesGet(IntegrationTestCase):

    @browsing
    def test_returns_list_of_uids(self, browser):
        self.login(self.administrator, browser=browser)

        favorite1 = create(Builder('favorite')
                           .for_user(self.administrator)
                           .for_object(self.branch_repofolder))

        favorite2 = create(Builder('favorite')
                           .for_user(self.administrator)
                           .for_object(self.leaf_repofolder))

        url = '{}/@repository-favorites/{}'.format(
            self.portal.absolute_url(), self.administrator.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEqual([favorite1.plone_uid, favorite2.plone_uid],
                         browser.json)

    @browsing
    def test_list_only_favorites_for_given_user(self, browser):
        self.login(self.administrator, browser=browser)

        favorite1 = create(Builder('favorite')
                           .for_user(self.administrator)
                           .for_object(self.branch_repofolder))

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.leaf_repofolder))

        url = '{}/@repository-favorites/{}'.format(
            self.portal.absolute_url(), self.administrator.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEqual([favorite1.plone_uid], browser.json)

    @browsing
    def test_list_only_repositoryfolder_favorites(self, browser):
        self.login(self.administrator, browser=browser)

        favorite1 = create(Builder('favorite')
                           .for_user(self.administrator)
                           .for_object(self.branch_repofolder))

        create(Builder('favorite')
               .for_user(self.administrator)
               .for_object(self.dossier))

        url = '{}/@repository-favorites/{}'.format(
            self.portal.absolute_url(), self.administrator.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEqual([favorite1.plone_uid], browser.json)

    @browsing
    def test_list_only_favorites_from_current_admin_unit(self, browser):
        self.login(self.administrator, browser=browser)

        favorite1 = create(Builder('favorite')
                           .for_user(self.administrator)
                           .for_object(self.branch_repofolder))

        create(Builder('favorite')
               .for_user(self.administrator)
               .for_object(self.leaf_repofolder)
               .having(admin_unit_id='sk'))

        url = '{}/@repository-favorites/{}'.format(
            self.portal.absolute_url(), self.administrator.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEqual([favorite1.plone_uid], browser.json)

    @browsing
    def test_raises_when_userid_is_missing(self, browser):
        self.login(self.administrator, browser=browser)

        with browser.expect_http_error(400):
            url = '{}/@repository-favorites'.format(self.portal.absolute_url())
            browser.open(url, method='GET',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {"message": "Must supply exactly one parameter (user id)",
             "type": "BadRequest"},
            browser.json)
