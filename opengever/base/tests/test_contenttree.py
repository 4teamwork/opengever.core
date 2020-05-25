from ftw.testbrowser import browsing
from mock import patch
from opengever.testing import IntegrationTestCase
import itertools


class TestContenttreeFetch(IntegrationTestCase):

    @patch('Products.ZCatalog.ZCatalog.ZCatalog.searchResults')
    @browsing
    def test_contenttree_fetch_returns_max_100_items(
        self, mocked_searchResults, browser
    ):
        self.login(self.regular_user, browser=browser)

        # Repeat the first item 200 times to have more than 100 results.
        def results(self, *args, **kwargs):
            results = self._catalog.searchResults(*args, **kwargs)
            return list(results) + list(itertools.repeat(results[0], 200))
        mocked_searchResults.side_effect = results

        url = (
            '{}/@@edit/++widget++form.widgets.IRelatedDocuments.relatedItems/'
            '@@contenttree-fetch'.format(self.document.absolute_url())
        )
        browser.open(
            url,
            method='POST',
            data={
                'href': '/'.join(self.repository_root.getPhysicalPath()),
                'rel': '0',
                'b_start': '0',
            },
        )
        self.assertEqual(len(browser.css('li.navTreeItem')), 100)

    @patch('Products.ZCatalog.ZCatalog.ZCatalog.searchResults')
    @browsing
    def test_contenttree_fetch_returns_items_from_b_start(
        self, mocked_searchResults, browser
    ):
        self.login(self.regular_user, browser=browser)

        # Repeat the first item 100 times for the first batch and the second
        # item 10 times for the second batch.
        def results(self, *args, **kwargs):
            results = self._catalog.searchResults(*args, **kwargs)
            return (
                list(itertools.repeat(results[0], 100))
                + list(itertools.repeat(results[1], 10))
            )
        mocked_searchResults.side_effect = results

        url = (
            '{}/@@edit/++widget++form.widgets.IRelatedDocuments.relatedItems/'
            '@@contenttree-fetch'.format(self.document.absolute_url())
        )
        browser.open(
            url,
            method='POST',
            data={
                'href': '/'.join(self.repository_root.getPhysicalPath()),
                'rel': '0',
                'b_start': '100',
            },
        )
        self.assertEqual(len(browser.css('li.navTreeItem')), 10)
        self.assertEqual(
            browser.css('li>a>span').first.text, 'rechnungsprufungskommission')
