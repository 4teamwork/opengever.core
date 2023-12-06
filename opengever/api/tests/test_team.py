from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.ogds.models.team import Team
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest
import json


class TestTeamGet(IntegrationTestCase):

    def setUp(self):
        super(TestTeamGet, self).setUp()
        self.team_id = Team.get_one(groupid='projekt_a').team_id

    @browsing
    def test_team_default_response(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal,
                     view='@teams/{}'.format(self.team_id),
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@teams/1',
             u'@type': u'virtual.ogds.team',
             u'active': True,
             u'group': {u'@id': u'http://nohost/plone/@ogds-groups/projekt_a',
                        u'@type': u'virtual.ogds.group',
                        u'active': True,
                        u'groupid': u'projekt_a',
                        u'groupname': u'projekt_a',
                        u'groupurl': u'http://nohost/plone/@groups/projekt_a',
                        u'is_local': False,
                        u'title': u'Projekt A'},
             u'groupid': u'projekt_a',
             u'items': [{u'@id': u'http://nohost/plone/@ogds-users/%s' % self.regular_user.id,
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
                         u'userid': self.regular_user.id,
                         u'username': self.regular_user.getUserName()},
                        {u'@id': u'http://nohost/plone/@ogds-users/%s' % self.dossier_responsible.id,
                         u'@type': u'virtual.ogds.user',
                         u'active': True,
                         u'department': None,
                         u'directorate': None,
                         u'email': u'%s@gever.local' % self.dossier_responsible.getUserName(),
                         u'email2': None,
                         u'firstname': u'Robert',
                         u'job_title': None,
                         u'lastname': u'Ziegler',
                         u'phone_fax': None,
                         u'phone_mobile': None,
                         u'phone_office': None,
                         u'title': u'Ziegler Robert',
                         u'userid': self.dossier_responsible.id,
                         u'username': self.dossier_responsible.getUserName()}],
             u'items_total': 2,
             u'org_unit_id': u'fa',
             u'org_unit_title': u'Finanz\xe4mt',
             u'team_id': 1,
             u'title': u'Projekt \xdcberbaung Dorfmatte'},
            browser.json)

    @browsing
    def test_raises_bad_request_when_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.portal,
                         view='@teams',
                         headers=self.api_headers)

    @browsing
    def test_raises_bad_request_when_too_many_params_are_given(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.portal,
                         view='@teams/{}/foobar'.format(self.team_id),
                         headers=self.api_headers)

    @browsing
    def test_batching_for_teams(self, browser):
        self.login(self.regular_user, browser=browser)
        team = Team.get_one(groupid='projekt_a')

        url = self.portal.absolute_url() + '/@teams/{}?b_size=2'.format(team.team_id)
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertNotIn('batching', browser.json)
        self.assertEquals(2, browser.json['items_total'])
        self.assertEquals(2, len(browser.json['items']))

        create(Builder('ogds_user').id('peter').in_group(team.group))
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertIn('batching', browser.json)
        self.assertEquals(3, browser.json['items_total'])
        self.assertEquals(2, len(browser.json['items']))


class TestTeamPost(IntegrationTestCase):

    valid_data = {
        'title': 'Team A',
        'active': True,
        'org_unit_id': {'token': 'fa', 'title': u'Finanz\xe4mt'},
        'groupid': {'token': 'projekt_a', 'title': u'Projekt A'}}

    @browsing
    def test_adding_a_team(self, browser):
        self.login(self.administrator, browser=browser)

        url = '{}/@teams'.format(self.portal.absolute_url())
        browser.open(url, method='POST', headers=self.api_headers,
                     data=json.dumps(self.valid_data))

        self.assertEquals(201, browser.status_code)
        self.assertEquals('http://nohost/plone/@teams/4', browser.headers.get('Location'))

    @browsing
    def test_limited_admin_can_add_a_team(self, browser):
        self.login(self.limited_admin, browser=browser)

        url = '{}/@teams'.format(self.portal.absolute_url())
        browser.open(url, method='POST', headers=self.api_headers,
                     data=json.dumps(self.valid_data))

        self.assertEquals(201, browser.status_code)
        self.assertEquals('http://nohost/plone/@teams/4', browser.headers.get('Location'))

    @browsing
    def test_validates_against_input(self, browser):
        self.login(self.administrator, browser=browser)

        self.valid_data['groupid'] = {'token': 'not-existing'}

        url = '{}/@teams'.format(self.portal.absolute_url())

        with browser.expect_http_error(400):
            browser.open(url, method='POST', headers=self.api_headers,
                         data=json.dumps(self.valid_data))

        self.assertEquals(
            {u'type': u'BadRequest',
             u'additional_metadata': {
                 u'fields': [
                     {u'field': u'groupid',
                      u'translated_message': u'Constraint not satisfied',
                      u'type': u'not-existing'}]},
             u'translated_message': u'Inputs not valid',
             u'message': u"[{'field': 'groupid', 'message': u'Constraint "
             "not satisfied', 'error': ConstraintNotSatisfied(u'not-existing')}]"},
            browser.json)

    @browsing
    def test_validates_required_fields(self, browser):
        self.login(self.administrator, browser=browser)

        self.valid_data.pop('groupid')

        url = '{}/@teams'.format(self.portal.absolute_url())
        with browser.expect_http_error(400):
            browser.open(url, method='POST', headers=self.api_headers,
                         data=json.dumps(self.valid_data))

        self.assertEquals(
            {u'type': u'BadRequest',
             u'additional_metadata': {
                 u'fields': [
                     {u'field': u'groupid',
                      u'translated_message': u'Required input is missing.',
                      u'type': u'groupid'}]
             },
             u'translated_message': u'Inputs not valid',
             u'message': u"[{'field': 'groupid', 'message': u'Required input is missing.', 'error': RequiredMissing('groupid')}]"},
            browser.json)


class TestTeamPatch(IntegrationTestCase):

    @browsing
    def test_update_a_team(self, browser):
        self.login(self.administrator, browser=browser)

        url = '{}/@teams/1'.format(self.portal.absolute_url())
        data = {'active': 'false',
                'groupid': {'token': 'projekt_b', 'title': 'Projekt b'}}
        browser.open(url, method='PATCH', headers=self.api_headers,
                     data=json.dumps(data))

        self.assertEquals(200, browser.status_code)

        team = Team.get(1)
        self.assertFalse(team.active)
        self.assertEquals('projekt_b', team.groupid)

    @browsing
    def test_limited_admin_can_update_a_team(self, browser):
        self.login(self.limited_admin, browser=browser)

        url = '{}/@teams/1'.format(self.portal.absolute_url())
        data = {'active': 'false',
                'groupid': {'token': 'projekt_b', 'title': 'Projekt b'}}
        browser.open(url, method='PATCH', headers=self.api_headers,
                     data=json.dumps(data))

        self.assertEquals(200, browser.status_code)

        team = Team.get(1)
        self.assertFalse(team.active)
        self.assertEquals('projekt_b', team.groupid)

    @browsing
    def test_validates_against_input(self, browser):
        self.login(self.administrator, browser=browser)

        url = '{}/@teams/1'.format(self.portal.absolute_url())
        data = {'active': 'false',
                'groupid': {'token': 'not-existing', 'title': 'Not existing'}}

        with browser.expect_http_error(400):
            browser.open(url, method='PATCH', headers=self.api_headers,
                         data=json.dumps(data))

        self.assertEquals(u'BadRequest', browser.json['type'])
        self.assertEquals(
            u'Inputs not valid', browser.json['translated_message'])
        self.assertEquals(
            {u'fields': [{u'field': u'groupid',
                          u'translated_message': u'Constraint not satisfied',
                          u'type': u'not-existing'}]},
            browser.json['additional_metadata'])

    @browsing
    def test_raises_not_found_for_not_existing_team(self, browser):
        self.login(self.administrator, browser=browser)

        url = '{}/@teams/39449'.format(self.portal.absolute_url())
        data = {'active': 'false',
                'groupid': {'token': 'projekt_b', 'title': 'Projekt b'}}

        with browser.expect_http_error(404):
            browser.open(url, method='PATCH', headers=self.api_headers,
                         data=json.dumps(data))

    @browsing
    def test_raises_bad_request_for_missing_team(self, browser):
        self.login(self.administrator, browser=browser)

        url = '{}/@teams'.format(self.portal.absolute_url())
        data = {'active': 'false',
                'groupid': {'token': 'projekt_b', 'title': 'Projekt b'}}

        with browser.expect_http_error(400):
            browser.open(url, method='PATCH', headers=self.api_headers,
                         data=json.dumps(data))

        self.assertEquals(
            {u'message': u'Must supply team ID as URL path parameter.',
             u'type': u'BadRequest'},
            browser.json)
