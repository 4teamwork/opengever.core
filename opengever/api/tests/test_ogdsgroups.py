from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest


class TestOGDSGroupsGet(IntegrationTestCase):

    @browsing
    def test_ogds_groups_default_response(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.contactfolder, view='@ogds-groups/projekt_a', headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/kontakte/@ogds-groups/projekt_a',
             u'@type': u'virtual.ogds.group',
             u'active': True,
             u'groupid': u'projekt_a',
             u'title': u'Projekt A',
             u'users': [{u'@id': u'http://nohost/plone/kontakte/@ogds-users/kathi.barfuss',
                         u'@type': u'virtual.ogds.user',
                         u'active': True,
                         u'department': u'Staatskanzlei',
                         u'directorate': u'Staatsarchiv',
                         u'email': u'foo@example.com',
                         u'email2': u'bar@example.com',
                         u'firstname': u'K\xe4thi',
                         u'lastname': u'B\xe4rfuss',
                         u'phone_fax': u'012 34 56 77',
                         u'phone_mobile': u'012 34 56 76',
                         u'phone_office': u'012 34 56 78',
                         u'title': u'B\xe4rfuss K\xe4thi',
                         u'userid': u'kathi.barfuss'},
                        {u'@id': u'http://nohost/plone/kontakte/@ogds-users/robert.ziegler',
                         u'@type': u'virtual.ogds.user',
                         u'active': True,
                         u'department': None,
                         u'directorate': None,
                         u'email': u'robert.ziegler@gever.local',
                         u'email2': None,
                         u'firstname': u'Robert',
                         u'lastname': u'Ziegler',
                         u'phone_fax': None,
                         u'phone_mobile': None,
                         u'phone_office': None,
                         u'title': u'Ziegler Robert',
                         u'userid': u'robert.ziegler'}]},
            browser.json)

    @browsing
    def test_raises_bad_request_when_groupid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.contactfolder, view='@ogds-groups', headers=self.api_headers)

    @browsing
    def test_raises_bad_request_when_too_many_params_are_given(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.contactfolder, view='@ogds-groups/projekt_a/foobar',
                         headers=self.api_headers)
