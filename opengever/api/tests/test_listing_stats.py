from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestListingStats(IntegrationTestCase):

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

        self.assertIn(
            'facet_pivot',
            browser.json.get('@components', {}).get('listing-stats', {}).keys(),
            'The listings-stats compoment should be expandend and include '
            'the `facet_pivot` property')

    @browsing
    def test_get_listing_stats_returns_a_pivot_query_for_listings(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            '{}/@listing-stats'.format(self.dossier.absolute_url()),
            headers={'Accept': 'application/json'},
        )

        self.assertItemsEqual(browser.json.keys(), ['@id', 'facet_pivot'])
