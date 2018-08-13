from ftw.testbrowser import browsing
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models.group import Group
from opengever.testing import IntegrationTestCase


class TestUserDetails(IntegrationTestCase):

    @browsing
    def test_user_details(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.portal, view='@@user-details/kathi.barfuss')

        self.assertEquals([u'B\xe4rfuss K\xe4thi (kathi.barfuss)'],
                          browser.css('h1.documentFirstHeading').text)

        metadata = dict(browser.css('.vertical').first.lists())
        self.assertDictContainsSubset({
            'Address': 'Kappelenweg 13 Postfach 1234 1234 Vorkappelen Schweiz',
            'Department': 'Staatskanzlei (SK)',
            'Description': 'nix',
            'Directorate': 'Staatsarchiv (Arch)',
            'Email': 'foo@example.com',
            'Email 2': 'bar@example.com',
            'Fax': '012 34 56 77',
            'Mobile phone': '012 34 56 76',
            'Name': u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
            'Office phone': '012 34 56 78',
            'Salutation': 'Prof. Dr.',
            'Teams': u'Projekt \xdcberbaung Dorfmatte',
            'URL': 'http://www.example.com',
        }, metadata)

    @browsing
    def test_parentheses_do_not_appear_without_abbreviation(self, browser):
        self.login(self.regular_user, browser)

        kathi = ogds_service().fetch_user('kathi.barfuss')
        kathi.department_abbr = None
        kathi.directorate_abbr = None

        browser.open(self.portal, view='@@user-details/kathi.barfuss')

        self.assertEquals([u'B\xe4rfuss K\xe4thi (kathi.barfuss)'],
                          browser.css('h1.documentFirstHeading').text)

        metadata = dict(browser.css('.vertical').first.lists())
        self.assertDictContainsSubset({
            'Department': 'Staatskanzlei',
            'Directorate': 'Staatsarchiv',
        }, metadata)

    @browsing
    def test_user_details_return_not_found_for_not_exisiting_user(self, browser):  # noqa
        with browser.expect_http_error(code=404):
            browser.login().open(self.portal, view='@@user-details/not.found')

    @browsing
    def test_list_all_team_memberships(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal, view='@@user-details/kathi.barfuss')

        self.assertEquals(
            [u'Projekt \xdcberbaung Dorfmatte'], browser.css('.teams li').text)
        self.assertEquals('http://nohost/plone/kontakte/team-1/view',
                          browser.css('.teams a').first.get('href'))

    @browsing
    def test_lists_group_memberships(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.portal, view='@@user-details/kathi.barfuss')

        self.assertEqual(
            ['fa_users', 'Projekt A'], browser.css('.groups li').text)

        group_links = [a.get('href') for a in browser.css('.groups li a')]
        self.assertEqual(
            ['http://nohost/plone/@@list_groupmembers?group=fa_users',
             'http://nohost/plone/@@list_groupmembers?group=projekt_a'],
            group_links)

    @browsing
    def test_urlencodes_group_member_urls(self, browser):
        self.login(self.regular_user, browser)
        user = self.get_ogds_user(self.regular_user)

        group_with_spaces = Group(groupid='with spaces')
        user.groups.append(group_with_spaces)

        browser.open(self.portal, view='@@user-details/kathi.barfuss')

        group_links = [a.get('href') for a in browser.css('.groups li a')]
        self.assertEqual(
            ['http://nohost/plone/@@list_groupmembers?group=fa_users',
             'http://nohost/plone/@@list_groupmembers?group=projekt_a',
             'http://nohost/plone/@@list_groupmembers?group=with+spaces'],
            group_links)


class TestUserDetailsPlain(IntegrationTestCase):

    @browsing
    def test_contains_only_metadata_table(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.portal, view='@@user-details-plain/kathi.barfuss')

        metadata = dict(browser.css('.vertical').first.lists())
        self.assertDictContainsSubset({
            'Address': 'Kappelenweg 13 Postfach 1234 1234 Vorkappelen Schweiz',
            'Department': 'Staatskanzlei (SK)',
            'Description': 'nix',
            'Directorate': 'Staatsarchiv (Arch)',
            'Email': 'foo@example.com',
            'Email 2': 'bar@example.com',
            'Fax': '012 34 56 77',
            'Mobile phone': '012 34 56 76',
            'Name': u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
            'Office phone': '012 34 56 78',
            'Salutation': 'Prof. Dr.',
            'Teams': u'Projekt \xdcberbaung Dorfmatte',
            'URL': 'http://www.example.com',
        }, metadata)

        self.assertEquals([], browser.css('h1'))
