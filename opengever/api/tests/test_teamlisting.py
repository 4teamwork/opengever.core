from ftw.testbrowser import browsing
from opengever.ogds.models.team import Team
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest


class TestTeamListingGet(IntegrationTestCase):

    @browsing
    def test_team_listing_default_response(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.contactfolder,
                     view='@team-listing',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual([
            {u'@id': u'http://nohost/plone/kontakte/@teams/1',
             u'@type': u'virtual.ogds.team',
             u'active': True,
             u'groupid': u'projekt_a',
             u'org_unit_id': u'fa',
             u'org_unit_title': u'Finanz\xe4mt',
             u'team_id': 1,
             u'title': u'Projekt \xdcberbaung Dorfmatte'},
            {u'@id': u'http://nohost/plone/kontakte/@teams/3',
             u'@type': u'virtual.ogds.team',
             u'active': True,
             u'groupid': u'projekt_laeaer',
             u'org_unit_id': u'fa',
             u'org_unit_title': u'Finanz\xe4mt',
             u'team_id': 3,
             u'title': u'Sekretariat Abteilung Null'},
            {u'@id': u'http://nohost/plone/kontakte/@teams/2',
             u'@type': u'virtual.ogds.team',
             u'active': True,
             u'groupid': u'projekt_b',
             u'org_unit_id': u'fa',
             u'org_unit_title': u'Finanz\xe4mt',
             u'team_id': 2,
             u'title': u'Sekretariat Abteilung XY'}],
            browser.json.get('items'))
        self.assertEqual(25, browser.json['b_size'])
        self.assertEqual(0, browser.json['b_start'])
        self.assertEqual({}, browser.json['facets'])
        self.assertEqual(3, browser.json['items_total'])

    @browsing
    def test_batch_teamlisting_offset(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.contactfolder,
                     view='@team-listing?b_size=2&b_start=1',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(2, len(browser.json['items']))
        self.assertEqual(
            [u'projekt_laeaer',
             u'projekt_b'],
            [each['groupid'] for each in browser.json['items']])
        self.assertEqual(2, browser.json['b_size'])
        self.assertEqual(1, browser.json['b_start'])
        self.assertEqual(3, browser.json['items_total'])

    @browsing
    def test_batch_large_offset_returns_empty_items(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.contactfolder,
                     view='@team-listing?b_start=999',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(0, len(browser.json['items']))
        self.assertEqual(25, browser.json['b_size'])
        self.assertEqual(999, browser.json['b_start'])
        self.assertEqual(3, browser.json['items_total'])

    @browsing
    def test_batch_size_maximum_is_100(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.contactfolder,
                     view='@team-listing?b_size=999',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(100, browser.json['b_size'])

    @browsing
    def test_batch_disallows_negative_size(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.contactfolder,
                         view='@team-listing?b_size=-1',
                         headers=self.api_headers)

    @browsing
    def test_batch_disallows_negative_start(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.contactfolder,
                         view='@team-listing?b_start=-1',
                         headers=self.api_headers)

    @browsing
    def test_state_filter_inactive_only(self, browser):
        self.login(self.regular_user, browser=browser)
        Team.get_one(groupid='projekt_a').active = False

        browser.open(self.contactfolder,
                     view='@team-listing?filters.state:record:list=inactive',
                     headers=self.api_headers)

        self.assertEqual(1, len(browser.json['items']))
        self.assertEqual(25, browser.json['b_size'])
        self.assertEqual(0, browser.json['b_start'])
        self.assertEqual(1, browser.json['items_total'])

    @browsing
    def test_state_filter_active_only(self, browser):
        self.login(self.regular_user, browser=browser)
        Team.get_one(groupid='projekt_a').active = False

        browser.open(self.contactfolder,
                     view='@team-listing?filters.state:record:list=active',
                     headers=self.api_headers)

        self.assertEqual(2, len(browser.json['items']))
        self.assertEqual(25, browser.json['b_size'])
        self.assertEqual(0, browser.json['b_start'])
        self.assertEqual(2, browser.json['items_total'])

    @browsing
    def test_state_filter_active_and_inactive(self, browser):
        self.login(self.regular_user, browser=browser)
        Team.get_one(groupid='projekt_a').active = False

        browser.open(self.contactfolder,
                     view='@team-listing'
                           '?filters.state:record:list=inactive'
                          '&filters.state:record:list=active',
                     headers=self.api_headers)

        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(25, browser.json['b_size'])
        self.assertEqual(0, browser.json['b_start'])
        self.assertEqual(3, browser.json['items_total'])

    @browsing
    def test_search_title(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.contactfolder,
                     view=u'@team-listing?search=\xdcberbaung',
                     headers=self.api_headers)

        self.assertEqual(1, len(browser.json['items']))
        self.assertEqual([
            {u'@id': u'http://nohost/plone/kontakte/@teams/1',
             u'@type': u'virtual.ogds.team',
             u'active': True,
             u'groupid': u'projekt_a',
             u'org_unit_id': u'fa',
             u'org_unit_title': u'Finanz\xe4mt',
             u'team_id': 1,
             u'title': u'Projekt \xdcberbaung Dorfmatte'}],
            browser.json['items'])
        self.assertEqual(1, browser.json['items_total'])

    @browsing
    def test_search_strips_asterisk(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.contactfolder,
                     view=u'@team-listing?search=XY*',
                     headers=self.api_headers)

        self.assertEqual(1, len(browser.json['items']))
        self.assertEqual(1, browser.json['items_total'])

    @browsing
    def test_sort_on_groupid(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.contactfolder,
                     view=u'@team-listing?sort_on=groupid',
                     headers=self.api_headers)

        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(
            [u'projekt_a', u'projekt_b', u'projekt_laeaer'],
            [each['groupid'] for each in browser.json['items']])
        self.assertEqual(3, browser.json['items_total'])

    @browsing
    def test_sort_descending(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.contactfolder,
                     view=u'@team-listing?sort_order=descending',
                     headers=self.api_headers)

        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(
            [u'Sekretariat Abteilung XY',
             u'Sekretariat Abteilung Null',
             u'Projekt \xdcberbaung Dorfmatte'],
            [each['title'] for each in browser.json['items'][:4]])
        self.assertEqual(3, browser.json['items_total'])
