from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_INTEGRATION_TESTING_THEME
from opengever.testing import IntegrationTestCase
from plone import api


class TestBaseURL(IntegrationTestCase):
    """These tests ensure that base URLs in GEVER behave the way we expect
    them to.

    Going forward, our frontend JS probably will rely mostly on the
    data-base-url attribute, but the <base /> tag is still present, and
    for example influences where a browser sends form POSTs to, so we assert
    on that as well.
    """

    layer = OPENGEVER_INTEGRATION_TESTING_THEME

    @browsing
    def test_data_base_url_attribute_is_present(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal)
        # Verify that Diazo doesn't drop the data-base-url attribute
        self.assertIn('data-base-url', browser.css('body').first.attrib)

    @browsing
    def test_data_base_url_attribute_contains_context_url_for_all_types(self, browser):
        # Using Manager to find/ have access to all sorts of objects
        self.login(self.manager, browser)

        catalog = api.portal.get_tool('portal_catalog')
        index = catalog._catalog.indexes['portal_type']
        distinct_portal_types = index.uniqueValues()

        # Get one object each for every distinct portal_type, and verify that
        # the data-base-url attribute actually contains the context's URL.
        for portal_type in distinct_portal_types:
            brains = api.content.find(portal_type=portal_type)
            obj = brains[0].getObject()
            browser.open(obj)
            data_base_url = browser.css('body').first.attrib.get('data-base-url')
            self.assertEqual(obj.absolute_url(), data_base_url)

    @browsing
    def test_base_url_tag_is_present(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal)
        # Ensure Plone didn't suddenly drop the <base /> tag
        self.assertIn('href', browser.css('head base').first.attrib)

    @browsing
    def test_base_url_tag_contains_context_url_with_trailing_slash(self, browser):
        # Using Manager to find/ have access to all sorts of objects
        self.login(self.manager, browser)

        catalog = api.portal.get_tool('portal_catalog')
        index = catalog._catalog.indexes['portal_type']
        distinct_portal_types = index.uniqueValues()

        # Get one object each for every distinct portal_type, and verify that
        # the <base /> tag contains the context's URL with trailing slash.
        for portal_type in distinct_portal_types:
            brains = api.content.find(portal_type=portal_type)
            obj = brains[0].getObject()
            browser.open(obj)
            base_url = browser.css('head base').first.attrib.get('href')
            self.assertEqual(base_url, obj.absolute_url().rstrip("/") + "/")
