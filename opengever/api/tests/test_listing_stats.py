from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.api.listing import FILTERS
from opengever.testing.integration_test_case import SolrIntegrationTestCase


class TestListingStats(SolrIntegrationTestCase):

    features = ['solr']

    def get_facet_pivot_for(self, obj, pivot_name, browser):
        """Returns a specific facet pivot for the given object
        """
        return browser.open(
            '{}/@listing-stats'.format(obj.absolute_url()),
            headers={'Accept': 'application/json'},
        ).json.get('facet_pivot', {}).get(pivot_name)

    def get_facet_by_value(self, pivot, value):
        return filter(lambda p: p.get('value') == value, pivot)[0]

    @browsing
    def test_listing_stats_id_in_components(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier.absolute_url(),
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json['@components']['listing-stats']['@id'],
            u'{}/@listing-stats'.format(self.dossier.absolute_url()))

    @browsing
    def test_listing_stats_is_expandable(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            '{}?expand=listing-stats'.format(self.dossier.absolute_url()),
            headers={'Accept': 'application/json'},
        )

        listing_stats = browser.json.get('@components', {}).get('listing-stats', {})
        listing_pivots = listing_stats.get('facet_pivot').get('listing_name')
        self.assertItemsEqual(
            map(lambda pivot: pivot.get('value'), listing_pivots),
            FILTERS.keys(),
            'The listings-stats compoment should be expandend and contain all '
            'listing filters')

    @browsing
    def test_listing_stats_full_response(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            '{}/@listing-stats'.format(self.dossier.absolute_url()),
            headers={'Accept': 'application/json'},
        )

        self.assertDictEqual(
            {
                u'@id': u'{}/@listing-stats'.format(self.dossier.absolute_url()),
                u'facet_pivot': {
                    u'listing_name': [
                        {u'count': 12, u'field': u'listing_name', u'value': u'documents'},
                        {u'count': 0, u'field': u'listing_name', u'value': u'workspaces'},
                        {u'count': 3, u'field': u'listing_name', u'value': u'dossiers'},
                        {u'count': 0, u'field': u'listing_name', u'value': u'contacts'},
                        {u'count': 9, u'field': u'listing_name', u'value': u'tasks'},
                        {u'count': 0, u'field': u'listing_name', u'value': u'workspace_folders'},
                        {u'count': 3, u'field': u'listing_name', u'value': u'proposals'},
                        {u'count': 0, u'field': u'listing_name', u'value': u'todos'},
                    ]
                }
            }, browser.json)

    @browsing
    def test_listing_stats_returns_total_counts(self, browser):
        self.login(self.regular_user, browser)

        dossier = create(Builder('dossier').within(self.leaf_repofolder))
        self.commit_solr()

        pivot = self.get_facet_pivot_for(dossier, 'listing_name', browser)

        self.assertEqual(0, sum([facet.get('count') for facet in pivot]))
        self.assertEqual(0, self.get_facet_by_value(pivot, 'dossiers').get('count'))

        subdossier = create(Builder('dossier').within(dossier))
        create(Builder('document').within(dossier))
        create(Builder('document').within(subdossier))
        create(Builder('document').within(subdossier))

        self.commit_solr()

        pivot = self.get_facet_pivot_for(dossier, 'listing_name', browser)

        self.assertEqual(4, sum([facet.get('count') for facet in pivot]))
        self.assertEqual(1, self.get_facet_by_value(pivot, 'dossiers').get('count'))
        self.assertEqual(3, self.get_facet_by_value(pivot, 'documents').get('count'))

    @browsing
    def test_exclude_trashed_content(self, browser):
        self.login(self.regular_user, browser)

        dossier = create(Builder('dossier').within(self.leaf_repofolder))
        document = create(Builder('document').within(dossier))

        self.commit_solr()

        browser.open(
            '{}/@listing-stats'.format(self.dossier.absolute_url()),
            headers={'Accept': 'application/json'},
        )

        pivot = self.get_facet_pivot_for(dossier, 'listing_name', browser)
        self.assertEqual(1, self.get_facet_by_value(pivot, 'documents').get('count'))

        browser.open(document.absolute_url() + '/@trash',
                     method='POST', headers={'Accept': 'application/json'})

        self.commit_solr()

        browser.open(
            '{}/@listing-stats'.format(self.dossier.absolute_url()),
            headers={'Accept': 'application/json'},
        )

        pivot = self.get_facet_pivot_for(dossier, 'listing_name', browser)
        self.assertEqual(0, self.get_facet_by_value(pivot, 'documents').get('count'))

    @browsing
    def test_listing_stats_pivot_queries_support(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            '{}/@listing-stats?queries=responsible:{}'.format(
                self.dossier.absolute_url(), self.regular_user.id),
            headers={'Accept': 'application/json'},
        )

        self.assertDictEqual(
            {
                u'@id': u'{}/@listing-stats'.format(self.dossier.absolute_url()),
                u'facet_pivot': {
                    u'listing_name': [
                        {u'count': 12, u'field':
                         u'listing_name',
                         u'value': u'documents',
                         u'queries': {u'responsible:kathi.barfuss': 1}},
                        {u'count': 0,
                         u'field': u'listing_name',
                         u'value': u'workspaces',
                         u'queries': {u'responsible:kathi.barfuss': 0}},
                        {u'count': 3,
                         u'field': u'listing_name',
                         u'value': u'dossiers',
                         u'queries': {u'responsible:kathi.barfuss': 0}},
                        {u'count': 0,
                         u'field': u'listing_name',
                         u'value': u'contacts',
                         u'queries': {u'responsible:kathi.barfuss': 0}},
                        {u'count': 9,
                         u'field': u'listing_name',
                         u'value': u'tasks',
                         u'queries': {u'responsible:kathi.barfuss': 8}},
                        {u'count': 0,
                         u'field': u'listing_name',
                         u'value': u'workspace_folders',
                         u'queries': {u'responsible:kathi.barfuss': 0}},
                        {u'count': 3,
                         u'field': u'listing_name',
                         u'value': u'proposals',
                         u'queries': {u'responsible:kathi.barfuss': 0}},
                        {u'count': 0,
                         u'field': u'listing_name',
                         u'value': u'todos',
                         u'queries': {u'responsible:kathi.barfuss': 0}},
                    ]
                }
            }, browser.json)
