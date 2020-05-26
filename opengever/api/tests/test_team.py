from ftw.testbrowser import browsing
from opengever.ogds.models.team import Team
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest


class TestTeamGet(IntegrationTestCase):

    def setUp(self):
        super(TestTeamGet, self).setUp()
        self.team_id = Team.get_one(groupid='projekt_a').team_id

    @browsing
    def test_team_default_response(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.contactfolder,
                     view='@team/{}'.format(self.team_id),
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/kontakte/@team/1',
             u'@type': u'virtual.ogds.team',
             u'active': True,
             u'group': {u'@id': u'http://nohost/plone/kontakte/@group/projekt_a',
                        u'@type': u'virtual.ogds.group',
                        u'active': True,
                        u'groupid': u'projekt_a',
                        u'title': u'Projekt A'},
             u'groupid': u'projekt_a',
             u'org_unit_id': u'fa',
             u'org_unit_title': u'Finanz\xe4mt',
             u'team_id': 1,
             u'title': u'Projekt \xdcberbaung Dorfmatte',
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
    def test_raises_bad_request_when_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.contactfolder,
                         view='@team',
                         headers=self.api_headers)

    @browsing
    def test_raises_bad_request_when_too_many_params_are_given(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.contactfolder,
                         view='@team/{}/foobar'.format(self.team_id),
                         headers=self.api_headers)
