from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest


class TestOGDSUserGet(IntegrationTestCase):

    @browsing
    def test_user_default_response(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.contactfolder,
                     view='@ogds-users/kathi.barfuss',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/kontakte/@ogds-users/kathi.barfuss',
             u'@type': u'virtual.ogds.user',
             u'active': True,
             u'address1': u'Kappelenweg 13',
             u'address2': u'Postfach 1234',
             u'city': u'Vorkappelen',
             u'country': u'Schweiz',
             u'department': u'Staatskanzlei',
             u'department_abbr': u'SK',
             u'description': u'nix',
             u'directorate': u'Staatsarchiv',
             u'directorate_abbr': u'Arch',
             u'email': u'foo@example.com',
             u'email2': u'bar@example.com',
             u'firstname': u'K\xe4thi',
             u'groups': [{u'@id': u'http://nohost/plone/kontakte/@ogds-groups/fa_users',
                          u'@type': u'virtual.ogds.group',
                          u'active': True,
                          u'groupid': u'fa_users',
                          u'title': u'fa Users Group'},
                         {u'@id': u'http://nohost/plone/kontakte/@ogds-groups/projekt_a',
                          u'@type': u'virtual.ogds.group',
                          u'active': True,
                          u'groupid': u'projekt_a',
                          u'title': u'Projekt A'}],
             u'import_stamp': None,
             u'lastname': u'B\xe4rfuss',
             u'phone_fax': u'012 34 56 77',
             u'phone_mobile': u'012 34 56 76',
             u'phone_office': u'012 34 56 78',
             u'salutation': u'Prof. Dr.',
             u'teams': [{u'@id': u'http://nohost/plone/kontakte/@teams/1',
                         u'@type': u'virtual.ogds.team',
                         u'active': True,
                         u'groupid': u'projekt_a',
                         u'org_unit_id': u'fa',
                         u'org_unit_title': u'Finanz\xe4mt',
                         u'team_id': 1,
                         u'title': u'Projekt \xdcberbaung Dorfmatte'}],
             u'url': u'http://www.example.com',
             u'userid': u'kathi.barfuss',
             u'zip_code': u'1234'},
            browser.json)

    @browsing
    def test_last_login_is_visible(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.contactfolder,
                     view='@ogds-users/{}'.format(self.administrator.getId()),
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertIn('last_login', browser.json)

    @browsing
    def test_raises_bad_request_when_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.contactfolder,
                         view='@ogds-users',
                         headers=self.api_headers)

    @browsing
    def test_raises_bad_request_when_too_many_params_are_given(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.contactfolder,
                         view='@ogds-users/kathi.barfuss/foobar',
                         headers=self.api_headers)
