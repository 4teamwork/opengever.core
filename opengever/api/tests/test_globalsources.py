from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.kub.testing import KuBIntegrationTestCase
from opengever.testing import IntegrationTestCase
import requests_mock


class TestGlobalSourcesGet(IntegrationTestCase):

    @browsing
    def test_globalsources_returns_a_list_of_all_globalsources(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@globalsources'.format(self.portal.absolute_url())
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            [{u'@id': u'http://nohost/plone/@globalsources/all_users_and_groups',
              u'title': u'all_users_and_groups'},
             {u'@id': u'http://nohost/plone/@globalsources/filtered_groups',
              u'title': u'filtered_groups'},
             {u'@id': u'http://nohost/plone/@globalsources/current_admin_unit_org_units',
              u'title': u'current_admin_unit_org_units'},
             {u'@id': u'http://nohost/plone/@globalsources/contacts',
              u'title': u'contacts'},
             {u'@id': u'http://nohost/plone/@globalsources/all_contacts',
              u'title': u'all_contacts'}],
            browser.json)

    @browsing
    def test_raises_not_found_for_not_existing_sources(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@globalsources/not-existing'.format(self.portal.absolute_url())

        with browser.expect_http_error(404):
            browser.open(url, headers=self.api_headers)

    @browsing
    def test_raises_bad_request_when_try_to_enumerate_source(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@globalsources/all_users_and_groups'.format(
            self.portal.absolute_url())

        with browser.expect_http_error(400):
            browser.open(url, headers=self.api_headers)

    @browsing
    def test_returns_batched_results(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@globalsources/all_users_and_groups?query=Rober'.format(
            self.portal.absolute_url())
        browser.open(url, headers=self.api_headers)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@globalsources/all_users_and_groups?query=Rober',
             u'items': [{u'title': u'Ziegler Robert (robert.ziegler)',
                         u'token': u'robert.ziegler'}],
             u'items_total': 1},
            browser.json)

    @browsing
    def test_all_users_and_groups_find_also_inactive_users_not_assigned_to_org_units(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('ogds_user').id('peter.inactive')
               .having(firstname='Peter', lastname='Inactive', active=False))

        url = '{}/@globalsources/all_users_and_groups?query=inacti'.format(
            self.portal.absolute_url())
        browser.open(url, headers=self.api_headers)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@globalsources/all_users_and_groups?query=inacti',
             u'items': [{u'title': u'Inactive Peter (peter.inactive)',
                         u'token': u'peter.inactive'},
                        {u'title': u'User Inactive (inactive.user)',
                         u'token': u'inactive.user'}],
             u'items_total': 2},
            browser.json)

    @browsing
    def test_all_users_and_groups_find_also_inactive_groups(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('ogds_group').having(groupid='inactive_group',
                                            title="Inaktiv",
                                            active=False))

        url = '{}/@globalsources/all_users_and_groups?query=inak'.format(
            self.portal.absolute_url())
        browser.open(url, headers=self.api_headers)
        self.assertEqual(
            {u'@id': u'http://nohost/plone/@globalsources/all_users_and_groups?query=inak',
             u'items': [{u'title': u'Inaktiv', u'token': u'group:inactive_group'}],
             u'items_total': 1},
            browser.json)


class TestGlobalSourcesGetInTeamraum(IntegrationTestCase):

    features = ('workspace', )

    @browsing
    def test_globalsources_returns_a_list_of_all_visible_globalsources(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@globalsources'.format(self.portal.absolute_url())
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual([], browser.json)

    @browsing
    def test_raises_not_found_for_not_visible_sources(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@globalsources/all_users_and_groups?query=Rober'.format(
            self.portal.absolute_url())

        self.deactivate_feature('workspace')
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.activate_feature('workspace')
        with browser.expect_http_error(404):
            browser.open(url, headers=self.api_headers)


@requests_mock.Mocker()
class TestGlobalSourcesGetWithKubContacts(KuBIntegrationTestCase):

    @browsing
    def test_query_contacts_shows_only_active_contacts(self, mocker, browser):
        create(Builder('ogds_user').id('jurgen.inactive')
               .having(firstname=u'K\xf6nig', lastname='Inactive', active=False))

        create(Builder('ogds_user').id('jurgen.active')
               .having(firstname=u'K\xf6nig', lastname='Active', active=True))

        self.login(self.regular_user, browser=browser)
        query_str = "K%C3%B6nig&is_active=True"
        url = self.mock_search(mocker, query_str)

        url = '{}/@globalsources/contacts?query=K%C3%B6nig'.format(
            self.portal.absolute_url())
        browser.open(url, headers=self.api_headers)

        self.assertEqual(
            [
                u'K\xf6nig KUB Active',
                u'K\xf6nig J\xfcrgen (jurgen.konig)',
                u'Active K\xf6nig (jurgen.active)'
            ],
            [item.get('title') for item in browser.json["items"]])

    @browsing
    def test_query_contacts_shows_all_contacts(self, mocker, browser):
        create(Builder('ogds_user').id('jurgen.inactive')
               .having(firstname=u'K\xf6nig', lastname='Inactive', active=False))

        create(Builder('ogds_user').id('jurgen.active')
               .having(firstname=u'K\xf6nig', lastname='Active', active=True))

        self.login(self.regular_user, browser=browser)
        query_str = "K%C3%B6nig"
        self.mock_search(mocker, query_str)

        url = '{}/@globalsources/all_contacts?query=K%C3%B6nig'.format(
            self.portal.absolute_url())
        browser.open(url, headers=self.api_headers)

        self.assertEqual(
            [
                u'K\xf6nig KUB Active',
                u'K\xf6nig KUB Inactive',
                u'K\xf6nig J\xfcrgen (jurgen.konig)',
                u'Inactive K\xf6nig (jurgen.inactive)',
                u'Active K\xf6nig (jurgen.active)'
            ],
            [item.get('title') for item in browser.json["items"]])
