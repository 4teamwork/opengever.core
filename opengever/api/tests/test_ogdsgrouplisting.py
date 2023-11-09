from ftw.testbrowser import browsing
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest


class TestOGDSGroupListingGet(IntegrationTestCase):

    @browsing
    def test_group_listing_default_response(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal,
                     view='@ogds-group-listing',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual([
            {u'@id': u'http://nohost/plone/@ogds-groups/committee_ver_group',
             u'@type': u'virtual.ogds.group',
             u'active': True,
             u'groupid': u'committee_ver_group',
             u'groupurl': u'http://nohost/plone/@groups/committee_ver_group',
             u'is_local': False,
             u'title': u'Gruppe Kommission f\xfcr Verkehr'},
            {u'@id': u'http://nohost/plone/@ogds-groups/committee_rpk_group',
             u'@type': u'virtual.ogds.group',
             u'active': True,
             u'groupid': u'committee_rpk_group',
             u'groupurl': u'http://nohost/plone/@groups/committee_rpk_group',
             u'is_local': False,
             u'title': u'Gruppe Rechnungspr\xfcfungskommission'}],
            browser.json.get('items')[:2])
        self.assertEqual(9, browser.json['items_total'])

    @browsing
    def test_batch_grouplisting_offset(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal,
                     view='@ogds-group-listing?b_size=4&b_start=2',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(4, len(browser.json['items']))
        self.assertEqual(
            [u'projekt_a',
             u'projekt_b',
             u'projekt_laeaer',
             u'fa_inbox_users'],
            [each['groupid'] for each in browser.json['items']])
        self.assertEqual(9, browser.json['items_total'])

    @browsing
    def test_batch_large_offset_returns_empty_items(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal,
                     view='@ogds-group-listing?b_start=999',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(0, len(browser.json['items']))
        self.assertEqual(9, browser.json['items_total'])

    @browsing
    def test_batch_disallows_negative_size(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.portal,
                         view='@ogds-group-listing?b_size=-1',
                         headers=self.api_headers)

    @browsing
    def test_batch_disallows_negative_start(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.portal,
                         view='@ogds-group-listing?b_start=-1',
                         headers=self.api_headers)

    @browsing
    def test_state_filter_inactive_only(self, browser):
        self.login(self.regular_user, browser=browser)

        ogds_service().fetch_group('projekt_a').active = False

        browser.open(self.portal,
                     view='@ogds-group-listing?filters.state:record:list=inactive',
                     headers=self.api_headers)

        self.assertEqual(
            [False],
            [group.get('active') for group in browser.json['items']])

    @browsing
    def test_state_filter_active_only(self, browser):
        self.login(self.regular_user, browser=browser)

        ogds_service().fetch_group('projekt_a').active = False

        browser.open(self.portal,
                     view='@ogds-group-listing?filters.state:record:list=active',
                     headers=self.api_headers)

        self.assertTrue(
            [True for i in range(8)],
            [group.get('active') for group in browser.json['items']])

    @browsing
    def test_state_filter_active_and_inactive(self, browser):
        self.login(self.regular_user, browser=browser)

        ogds_service().fetch_group('projekt_a').active = False

        browser.open(self.portal,
                     view='@ogds-group-listing'
                          '?filters.state:record:list=inactive'
                          '&filters.state:record:list=active',
                     headers=self.api_headers)

        self.assertEqual(9, len(browser.json['items']))
        self.assertEqual(9, browser.json['items_total'])

    @browsing
    def test_filter_by_local_only(self, browser):
        self.login(self.regular_user, browser=browser)

        ogds_service().fetch_group('projekt_a').is_local = True
        ogds_service().fetch_group('projekt_b').is_local = None
        ogds_service().fetch_group('projekt_laeaer').is_local = False

        browser.open(self.portal,
                     view='@ogds-group-listing?filters.is_local:record:boolean=True',
                     headers=self.api_headers)

        self.assertEqual(
            [u'projekt_a'],
            [group.get('groupid') for group in browser.json['items']])

    @browsing
    def test_filter_by_non_lcoal_only(self, browser):
        self.login(self.regular_user, browser=browser)

        ogds_service().fetch_group('projekt_a').is_local = True
        ogds_service().fetch_group('projekt_b').is_local = None
        ogds_service().fetch_group('projekt_laeaer').is_local = False

        browser.open(self.portal,
                     view='@ogds-group-listing?filters.is_local:record:boolean=False',
                     headers=self.api_headers)

        groupids = [group.get('groupid') for group in browser.json['items']]
        self.assertNotIn('projekt_a', groupids)
        self.assertIn('projekt_b', groupids)
        self.assertIn('projekt_laeaer', groupids)

    @browsing
    def test_search_title(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal,
                     view=u'@ogds-group-listing?search=Projekt',
                     headers=self.api_headers)

        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(
            [u'projekt_a', u'projekt_b', u'projekt_laeaer'],
            [group.get('groupid') for group in browser.json['items']])
        self.assertEqual(3, browser.json['items_total'])

    @browsing
    def test_search_strips_asterisk(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal,
                     view=u'@ogds-group-listing?search=Projekt*',
                     headers=self.api_headers)

        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(3, browser.json['items_total'])

    @browsing
    def test_sort_descending(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal,
                     view=u'@ogds-group-listing?sort_order=descending',
                     headers=self.api_headers)

        self.assertEqual(9, len(browser.json['items']))
        self.assertEqual(
            [u'rk Users Group', u'rk Inbox Users Group', u'fa Users Group', u'fa Inbox Users Group'],
            [each['title'] for each in browser.json['items'][:4]])
        self.assertEqual(9, browser.json['items_total'])
