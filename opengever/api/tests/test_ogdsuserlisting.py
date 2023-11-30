from datetime import date
from ftw.testbrowser import browsing
from opengever.ogds.models.service import ogds_service
from opengever.ogds.models.user import User
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest


class TestOGDSUserListingGet(IntegrationTestCase):

    @browsing
    def test_user_listing_default_response(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal,
                     view='@ogds-user-listing',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual([
            {u'@id': u'http://nohost/plone/@ogds-users/kathi.barfuss',
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
             u'userid': u'kathi.barfuss',
             u'username': u'kathi.barfuss'},
            {u'@id': u'http://nohost/plone/@ogds-users/james.bond',
             u'@type': u'virtual.ogds.user',
             u'active': True,
             u'department': None,
             u'directorate': None,
             u'email': u'james.bond@gever.local',
             u'email2': None,
             u'firstname': u'James',
             u'job_title': None,
             u'lastname': u'B\xf6nd',
             u'phone_fax': None,
             u'phone_mobile': None,
             u'phone_office': None,
             u'title': u'B\xf6nd James',
             u'userid': u'james.bond',
             u'username': u'james.bond'}],
            browser.json.get('items')[1:3])
        self.assertEqual(23, browser.json['items_total'])

    @browsing
    def test_last_login_is_visible_in_ogds_user_listing(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.portal,
                     view='@ogds-user-listing',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertIn('last_login', browser.json.get('items')[0])

    @browsing
    def test_batch_userlisting_offset(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal,
                     view='@ogds-user-listing?b_size=4&b_start=7',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(4, len(browser.json['items']))
        self.assertItemsEqual(
            [self.workspace_admin.getId(),
             self.limited_admin.getId(),
             self.meeting_user.getId(),
             self.administrator.getId(),],
            [each['userid'] for each in browser.json['items']])
        self.assertEqual(23, browser.json['items_total'])

    @browsing
    def test_batch_large_offset_returns_empty_items(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal,
                     view='@ogds-user-listing?b_start=999',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(0, len(browser.json['items']))
        self.assertEqual(23, browser.json['items_total'])

    @browsing
    def test_batch_disallows_negative_size(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.portal,
                         view='@ogds-user-listing?b_size=-1',
                         headers=self.api_headers)

    @browsing
    def test_batch_disallows_negative_start(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.portal,
                         view='@ogds-user-listing?b_start=-1',
                         headers=self.api_headers)

    @browsing
    def test_state_filter_inactive_only(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal,
                     view='@ogds-user-listing?filters.state:record:list=inactive',
                     headers=self.api_headers)

        self.assertEqual(1, len(browser.json['items']))
        self.assertEqual(1, browser.json['items_total'])

    @browsing
    def test_state_filter_active_only(self, browser):
        self.login(self.regular_user, browser=browser)
        ogds_user = self.get_ogds_user(self.reader_user)
        ogds_user.active = False

        browser.open(self.portal,
                     view='@ogds-user-listing?filters.state:record:list=active',
                     headers=self.api_headers)

        self.assertEqual(21, len(browser.json['items']))
        self.assertEqual(21, browser.json['items_total'])

    @browsing
    def test_state_filter_active_and_inactive(self, browser):
        self.login(self.regular_user, browser=browser)
        ogds_user = self.get_ogds_user(self.reader_user)
        ogds_user.active = False

        browser.open(self.portal,
                     view='@ogds-user-listing'
                          '?filters.state:record:list=inactive'
                          '&filters.state:record:list=active',
                     headers=self.api_headers)

        self.assertEqual(23, len(browser.json['items']))
        self.assertEqual(23, browser.json['items_total'])

    @browsing
    def test_last_login_filter(self, browser):
        self.login(self.regular_user, browser=browser)
        filters_expression = 'filters.last_login:record:list=2020-01-01%20TO%202020-04-04'
        browser.open(self.portal,
                     view='@ogds-user-listing?{}'.format(filters_expression),
                     headers=self.api_headers)
        self.assertEqual(0, len(browser.json['items']))

        User.query.get_by_userid(self.meeting_user.getId()).last_login = date(2020, 3, 2)
        User.query.get_by_userid(self.dossier_responsible.getId()).last_login = date(2020, 2, 5)
        browser.open(self.portal,
                     view='@ogds-user-listing?{}'.format(filters_expression),
                     headers=self.api_headers)

        self.assertEqual(2, len(browser.json['items']))

        User.query.get_by_userid(self.dossier_responsible.getId()).last_login = date(2020, 5, 5)
        browser.open(self.portal,
                     view='@ogds-user-listing?{}'.format(filters_expression),
                     headers=self.api_headers)
        self.assertEqual(1, len(browser.json['items']))

    @browsing
    def test_search_firstname(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal,
                     view=u'@ogds-user-listing?search=L\xfcck',
                     headers=self.api_headers)

        self.assertEqual(1, len(browser.json['items']))
        self.assertEqual([
            {u'@id': u'http://nohost/plone/@ogds-users/lucklicher.laser',
             u'@type': u'virtual.ogds.user',
             u'active': True,
             u'department': None,
             u'directorate': None,
             u'email': u'lucklicher.laser@gever.local',
             u'email2': None,
             u'firstname': u'L\xfccklicher',
             u'job_title': None,
             u'lastname': u'L\xe4ser',
             u'phone_fax': None,
             u'phone_mobile': None,
             u'phone_office': None,
             u'title': u'L\xe4ser L\xfccklicher',
             u'userid': u'lucklicher.laser',
             u'username': u'lucklicher.laser'}],
            browser.json['items'])
        self.assertEqual(1, browser.json['items_total'])

    @browsing
    def test_search_fristname_and_lastname(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal,
                     view=u'@ogds-user-listing?search=frido gentobler',
                     headers=self.api_headers)

        self.assertEqual(1, len(browser.json['items']))
        self.assertEqual([
            {u'@id': u'http://nohost/plone/@ogds-users/fridolin.hugentobler',
             u'@type': u'virtual.ogds.user',
             u'active': True,
             u'department': None,
             u'directorate': None,
             u'email': u'fridolin.hugentobler@gever.local',
             u'email2': None,
             u'firstname': u'Fridolin',
             u'job_title': None,
             u'lastname': u'Hugentobler',
             u'phone_fax': None,
             u'phone_mobile': None,
             u'phone_office': None,
             u'title': u'Hugentobler Fridolin',
             u'userid': u'fridolin.hugentobler',
             u'username': u'fridolin.hugentobler'}],
            browser.json['items'])
        self.assertEqual(1, browser.json['items_total'])

    @browsing
    def test_search_strips_asterisk(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal,
                     view=u'@ogds-user-listing?search=gentobler*',
                     headers=self.api_headers)

        self.assertEqual(1, len(browser.json['items']))
        self.assertEqual(1, browser.json['items_total'])

    @browsing
    def test_sort_on_firstname(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal,
                     view=u'@ogds-user-listing?sort_on=firstname',
                     headers=self.api_headers)

        self.assertEqual(23, len(browser.json['items']))
        self.assertEqual(
            [u'B\xe9atrice', u'C\xf6mmittee', u'David', u'Fridolin'],
            [each['firstname'] for each in browser.json['items'][1:5]])
        self.assertEqual(23, browser.json['items_total'])

    @browsing
    def test_listing_always_has_a_secondary_sort_by_userid(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal,
                     view=u'@ogds-user-listing?sort_on=department',
                     headers=self.api_headers)

        subset = [item['userid'] for item in browser.json['items']
                  if item['department'] is None]
        self.assertEqual(22, len(subset))
        self.assertEqual(23, browser.json['items_total'])

        expected = sorted([item.userid for item in User.query.all()
                           if item.department is None])
        self.assertEqual(subset, expected)

    @browsing
    def test_secondary_sort_by_userid_respects_sort_order(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.portal,
            view=u'@ogds-user-listing?sort_on=department&sort_order=descending',
            headers=self.api_headers)

        subset = [item['userid'] for item in browser.json['items']
                  if item['department'] is None]
        self.assertEqual(22, len(subset))
        self.assertEqual(23, browser.json['items_total'])

        expected = sorted(
            [item.userid for item in User.query.all() if item.department is None],
            reverse=True)
        self.assertEqual(subset, expected)

    @browsing
    def test_sort_descending(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal,
                     view=u'@ogds-user-listing?sort_order=descending',
                     headers=self.api_headers)

        self.assertEqual(23, len(browser.json['items']))
        self.assertEqual(
            [u'Ziegler', u'User', 'User', u'Secretary', u'Schr\xf6dinger'],
            [each['lastname'] for each in browser.json['items'][:5]])
        self.assertEqual(23, browser.json['items_total'])

    @browsing
    def test_handles_non_ascii_userids(self, browser):
        self.login(self.regular_user, browser=browser)

        ogds_user = User.query.get_by_userid(self.reader_user.id)
        ogds_user.userid = u'l\xfccklicher.laser'

        browser.open(self.portal,
                     view=u'@ogds-user-listing?search=L\xfcck',
                     headers=self.api_headers)

        self.assertEqual(1, len(browser.json['items']))
        self.assertEqual([
            {u'@id': u'http://nohost/plone/@ogds-users/l\xfccklicher.laser',
             u'@type': u'virtual.ogds.user',
             u'active': True,
             u'department': None,
             u'directorate': None,
             u'email': u'lucklicher.laser@gever.local',
             u'email2': None,
             u'firstname': u'L\xfccklicher',
             u'job_title': None,
             u'lastname': u'L\xe4ser',
             u'phone_fax': None,
             u'phone_mobile': None,
             u'phone_office': None,
             u'title': u'L\xe4ser L\xfccklicher',
             u'userid': u'l\xfccklicher.laser',
             u'username': u'lucklicher.laser'}],
            browser.json['items'])
        self.assertEqual(1, browser.json['items_total'])

    @browsing
    def test_filter_by_group_membership(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal,
                     view='@ogds-user-listing?filters.groupid:record=projekt_a',
                     headers=self.api_headers)

        self.assertEqual(2, len(browser.json['items']))
        self.assertEqual(2, browser.json['items_total'])
        group = ogds_service().fetch_group("projekt_a")
        self.assertEqual(
            [user.userid for user in group.users],
            [user['userid'] for user in browser.json['items']])

    @browsing
    def test_sorting_when_filtering_by_group_membership(self, browser):
        self.login(self.regular_user, browser=browser)
        group = ogds_service().fetch_group("projekt_a")
        group.users.append(ogds_service().fetch_user(self.meeting_user.getId()))
        self.assertEqual(3, len(group.users))

        browser.open(
            self.portal,
            view='@ogds-user-listing?filters.groupid:record=projekt_a&sort_on=lastname',
            headers=self.api_headers)
        self.assertEqual(
            sorted([user.lastname for user in group.users]),
            [user['lastname'] for user in browser.json['items']])

        browser.open(
            self.portal,
            view='@ogds-user-listing?filters.groupid:record=projekt_a&sort_on=lastname&sort_order=reverse',
            headers=self.api_headers)
        self.assertEqual(
            sorted([user.lastname for user in group.users], reverse=True),
            [user['lastname'] for user in browser.json['items']])

        browser.open(
            self.portal,
            view='@ogds-user-listing?filters.groupid:record=projekt_a&sort_on=userid&sort_order=reverse',
            headers=self.api_headers)
        self.assertEqual(
            sorted([user.userid for user in group.users], reverse=True),
            [user['userid'] for user in browser.json['items']])
