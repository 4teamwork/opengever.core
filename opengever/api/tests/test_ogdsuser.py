from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.api.serializer import SerializeUserModelToJson
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.models.group import Group
from opengever.ogds.models.tests.base import OGDSTestCase
from opengever.ogds.models.user import User
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest


class TestOGDSUserGet(IntegrationTestCase):

    @browsing
    def test_user_default_response(self, browser):
        self.login(self.regular_user, browser=browser)

        group_a = Group.query.filter(Group.groupid == 'projekt_a').one()

        # Groups without a title
        create(
            Builder('ogds_group')
            .having(groupid='a_project', title=None, users=group_a.users)
            )
        create(
            Builder('ogds_group')
            .having(groupid='z_project', title=None, users=group_a.users)
            )

        create(
            Builder('ogds_team')
            .having(
                title=u'Analyse Systemumgebung',
                group=group_a,
                org_unit=get_current_org_unit(),
                )
            )

        create(
            Builder('ogds_team')
            .having(
                title=u'Zentrale Dienste',
                group=group_a,
                org_unit=get_current_org_unit(),
                )
            )

        browser.open(self.portal,
                     view='@ogds-users/kathi.barfuss',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@ogds-users/kathi.barfuss',
             u'@type': u'virtual.ogds.user',
             u'absent': False,
             u'absent_from': None,
             u'absent_to': None,
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
             u'display_name': u'B\xe4rfuss K\xe4thi',
             u'email': u'foo@example.com',
             u'email2': u'bar@example.com',
             u'external_id': u'kathi.barfuss',
             u'firstname': u'K\xe4thi',
             u'groups': [{u'@id': u'http://nohost/plone/@ogds-groups/projekt_a',
                          u'@type': u'virtual.ogds.group',
                          u'active': True,
                          u'groupid': u'projekt_a',
                          u'groupurl': u'http://nohost/plone/@groups/projekt_a',
                          u'is_local': False,
                          u'title': u'Projekt A'},
                         {u'@id': u'http://nohost/plone/@ogds-groups/a_project',
                          u'@type': u'virtual.ogds.group',
                          u'active': True,
                          u'groupid': u'a_project',
                          u'groupurl': u'http://nohost/plone/@groups/a_project',
                          u'is_local': False,
                          u'title': None},
                         {u'@id': u'http://nohost/plone/@ogds-groups/fa_users',
                          u'@type': u'virtual.ogds.group',
                          u'active': True,
                          u'groupid': u'fa_users',
                          u'groupurl': u'http://nohost/plone/@groups/fa_users',
                          u'is_local': False,
                          u'title': u'fa Users Group'},
                         {u'@id': u'http://nohost/plone/@ogds-groups/z_project',
                          u'@type': u'virtual.ogds.group',
                          u'active': True,
                          u'groupid': u'z_project',
                          u'groupurl': u'http://nohost/plone/@groups/z_project',
                          u'is_local': False,
                          u'title': None}],
             u'job_title': u'Gesch\xe4ftsf\xfchrerin',
             u'lastname': u'B\xe4rfuss',
             u'phone_fax': u'012 34 56 77',
             u'phone_mobile': u'012 34 56 76',
             u'phone_office': u'012 34 56 78',
             u'object_sid': None,
             u'organization': None,
             u'salutation': u'Frau',
             u'teams': [{u'@id': u'http://nohost/plone/@teams/4',
                         u'@type': u'virtual.ogds.team',
                         u'active': True,
                         u'groupid': 'projekt_a',
                         u'org_unit_id': u'fa',
                         u'org_unit_title': u'Finanz\xe4mt',
                         u'team_id': 4,
                         u'title': u'Analyse Systemumgebung'},
                        {u'@id': u'http://nohost/plone/@teams/1',
                         u'@type': u'virtual.ogds.team',
                         u'active': True,
                         u'groupid': u'projekt_a',
                         u'org_unit_id': u'fa',
                         u'org_unit_title': u'Finanz\xe4mt',
                         u'team_id': 1,
                         u'title': u'Projekt \xdcberbaung Dorfmatte'},
                        {u'@id': u'http://nohost/plone/@teams/5',
                         u'@type': u'virtual.ogds.team',
                         u'active': True,
                         u'groupid': 'projekt_a',
                         u'org_unit_id': u'fa',
                         u'org_unit_title': u'Finanz\xe4mt',
                         u'team_id': 5,
                         u'title': u'Zentrale Dienste'}],
             u'url': u'http://www.example.com',
             u'userid': u'kathi.barfuss',
             u'username': u'kathi.barfuss',
             u'zip_code': u'1234'},
            browser.json)

    @browsing
    def test_last_login_is_visible(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.portal,
                     view='@ogds-users/{}'.format(self.administrator.getId()),
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertIn('last_login', browser.json)

    @browsing
    def test_raises_bad_request_when_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.portal,
                         view='@ogds-users',
                         headers=self.api_headers)

    @browsing
    def test_raises_bad_request_when_too_many_params_are_given(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.portal,
                         view='@ogds-users/kathi.barfuss/foobar',
                         headers=self.api_headers)

    @browsing
    def test_handles_non_ascii_userids(self, browser):
        self.login(self.regular_user, browser=browser)

        ogds_user = User.query.get_by_userid(self.reader_user.id)
        ogds_user.userid = u'l\xfccklicher.laser'

        browser.open(u'http://nohost/plone/@ogds-users/l\xfccklicher.laser',
                     headers=self.api_headers)

        self.assertEqual(
            u'http://nohost/plone/@ogds-users/l%C3%BCcklicher.laser',
            browser.json['@id'])

        self.assertEqual(
            u'l\xfccklicher.laser',
            browser.json['userid'])


class TestAssignedGroupsMethod(OGDSTestCase):

    def test_assigned_groups_returns_empty_list_if_no_groups_are_assigned(self):
        serializer = SerializeUserModelToJson(self.bob, None)
        self.assertEqual([], serializer.assigned_groups())

    def test_assigned_groups_returns_a_list_of_multiple_groups(self):
        serializer = SerializeUserModelToJson(self.john, None)
        groups = serializer.assigned_groups()
        self.assertSequenceEqual([self.members_a, self.inbox_members], groups)

    def test_assigned_groups_is_ordered_by_group_title(self):
        self.members_a.title = 'Group B'
        self.inbox_members.title = 'Group C'

        create(Builder("ogds_group").id("members_1")
               .having(title='Group A', users=[self.john]))
        create(Builder("ogds_group").id("members_z")
               .having(title='Group D', users=[self.john]))

        serializer = SerializeUserModelToJson(self.john, None)
        groups = serializer.assigned_groups()

        self.assertSequenceEqual(['Group A', 'Group B', 'Group C', 'Group D'],
                                 [group.title for group in groups])


class TestAssignedTeamsMethod(OGDSTestCase):

    def test_assigned_teams_returns_empty_list_if_no_teams_are_assigned(self):
        serializer = SerializeUserModelToJson(self.bob, None)
        self.assertEqual([], serializer.assigned_teams())

    def test_assigned_teams_returns_a_list_of_multiple_teams(self):
        team_a = create(Builder("ogds_team").having(title="Team A",
                                                    group=self.members_a,
                                                    org_unit=self.org_unit_a))

        team_b = create(Builder("ogds_team").having(title="Team B",
                                                    group=self.members_a,
                                                    org_unit=self.org_unit_a))

        create(Builder("ogds_team").having(title="Team C",
                                           group=self.members_b,
                                           org_unit=self.org_unit_a))

        serializer = SerializeUserModelToJson(self.john, None)
        teams = serializer.assigned_teams()
        self.assertItemsEqual([team_a, team_b], teams)

    def test_assigned_teams_is_ordered_by_team_title(self):
        create(Builder("ogds_team").having(title="Team A",
                                           group=self.members_a,
                                           org_unit=self.org_unit_a))

        create(Builder("ogds_team").having(title="Team C",
                                           group=self.members_a,
                                           org_unit=self.org_unit_a))

        create(Builder("ogds_team").having(title="Team D",
                                           group=self.members_a,
                                           org_unit=self.org_unit_a))

        create(Builder("ogds_team").having(title="Team B",
                                           group=self.members_a,
                                           org_unit=self.org_unit_a))

        serializer = SerializeUserModelToJson(self.john, None)
        teams = serializer.assigned_teams()

        self.assertSequenceEqual(['Team A', 'Team B', 'Team C', 'Team D'],
                                 [team.title for team in teams])
