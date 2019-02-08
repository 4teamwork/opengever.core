from opengever.testing import IntegrationTestCase
from ftw.testbrowser import browsing
from plone import api
from opengever.base.interfaces import IReferenceNumberSettings


class TestGeverTabMixin(IntegrationTestCase):

    @browsing
    def test_reference_number_custom_sort(self, browser):
        self.login(self.regular_user)

        api.portal.set_registry_record(
            name='formatter',
            value='grouped_by_three',
            interface=IReferenceNumberSettings)

        listing_view = self.leaf_repofolder.restrictedTraverse(
            'tabbedview_view-dossiers')

        results = listing_view.custom_sort(
            ['OG 921.11-2', 'OG 921.11-1', 'OG 921.11-12', 'OG 921.11-11'],
            sort_on='reference', sort_reverse=False)

        self.assertEquals(
            ['OG 921.11-1', 'OG 921.11-2', 'OG 921.11-11', 'OG 921.11-12'],
            results)

    @browsing
    def test_subject_filter_widget_returns_empty_string_by_default(self, browser):
        self.login(self.regular_user)

        listing_view = self.leaf_repofolder.restrictedTraverse(
            'tabbedview_view-dossiers')

        self.assertEquals('', listing_view.subject_filter_widget())

    @browsing
    def test_subject_filter_widget_returns_empty_string_if_available_without_solr(self, browser):
        self.login(self.regular_user)

        listing_view = self.leaf_repofolder.restrictedTraverse(
            'tabbedview_view-dossiers')
        listing_view.subject_filter_available = True

        self.assertEquals('', listing_view.subject_filter_widget())

    @browsing
    def test_subject_filter_widget_returns_widget_if_available_with_solr(self, browser):
        self.login(self.regular_user)
        self.activate_feature('solr')
        self.mock_solr(response_json={
            u'facet_counts': {u'facet_fields': {u'Subject': ['Foo']}}})

        listing_view = self.leaf_repofolder.restrictedTraverse(
            'tabbedview_view-dossiers')

        browser.open_html(listing_view.subject_filter_widget())

        self.assertEqual(
            1, len(browser.css('.keyword-widget')))
