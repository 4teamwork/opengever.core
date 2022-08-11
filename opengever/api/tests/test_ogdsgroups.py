from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest


class TestOGDSGroupsGet(IntegrationTestCase):

    @browsing
    def test_ogds_groups_default_response(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal, view='@ogds-groups/projekt_a', headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@ogds-groups/projekt_a',
             u'@type': u'virtual.ogds.group',
             u'active': True,
             u'groupid': u'projekt_a',
             u'groupurl': u'http://nohost/plone/@groups/projekt_a',
             u'is_local': False,
             u'title': u'Projekt A',
             u'items': [{u'@id': u'http://nohost/plone/@ogds-users/kathi.barfuss',
                         u'@type': u'virtual.ogds.user',
                         u'active': True,
                         u'department': u'Staatskanzlei',
                         u'directorate': u'Staatsarchiv',
                         u'email': u'foo@example.com',
                         u'email2': u'bar@example.com',
                         u'firstname': u'K\xe4thi',
                         u'job_title': u'Gesch\xe4ftsf\xfchrerin',
                         u'lastname': u'B\xe4rfuss',
                         u'phone_fax': u'012 34 56 77',
                         u'phone_mobile': u'012 34 56 76',
                         u'phone_office': u'012 34 56 78',
                         u'title': u'B\xe4rfuss K\xe4thi',
                         u'userid': u'kathi.barfuss'},
                        {u'@id': u'http://nohost/plone/@ogds-users/robert.ziegler',
                         u'@type': u'virtual.ogds.user',
                         u'active': True,
                         u'department': None,
                         u'directorate': None,
                         u'email': u'robert.ziegler@gever.local',
                         u'email2': None,
                         u'firstname': u'Robert',
                         u'job_title': None,
                         u'lastname': u'Ziegler',
                         u'phone_fax': None,
                         u'phone_mobile': None,
                         u'phone_office': None,
                         u'title': u'Ziegler Robert',
                         u'userid': u'robert.ziegler'}],
             u'items_total': 2},
            browser.json)

    @browsing
    def test_ogds_groups_users_are_sorted(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal, view='@ogds-groups/projekt_a',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            [u'B\xe4rfuss', u'Ziegler'],
            [each['lastname'] for each in browser.json['items']])

        group = ogds_service().fetch_group("projekt_a")
        group.users.append(ogds_service().fetch_user(self.workspace_member.getId()))

        browser.open(self.portal, view='@ogds-groups/projekt_a',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            [u'B\xe4rfuss', u'Schr\xf6dinger', u'Ziegler'],
            [each['lastname'] for each in browser.json['items']])

    @browsing
    def test_raises_bad_request_when_groupid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.portal, view='@ogds-groups', headers=self.api_headers)

    @browsing
    def test_raises_bad_request_when_too_many_params_are_given(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.portal, view='@ogds-groups/projekt_a/foobar',
                         headers=self.api_headers)

    @browsing
    def test_batching_for_ogds_groups(self, browser):
        self.login(self.regular_user, browser=browser)
        projekt_a = ogds_service().fetch_group('projekt_a')
        url = self.portal.absolute_url() + '/@ogds-groups/projekt_a?b_size=2'
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertNotIn('batching', browser.json)
        self.assertEquals(2, browser.json['items_total'])
        self.assertEquals(2, len(browser.json['items']))

        create(Builder('ogds_user').id('peter').in_group(projekt_a))
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertIn('batching', browser.json)
        self.assertEquals(3, browser.json['items_total'])
        self.assertEquals(2, len(browser.json['items']))
