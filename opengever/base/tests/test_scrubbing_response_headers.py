from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_REQUESTS
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ZSERVER_TESTING
from opengever.testing import FunctionalTestCase


class TestResponseHeaderScrubbing(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ZSERVER_TESTING

    @browsing
    def test_server_version_details_are_scrubbed_out(self, browser):
        browser.allow_redirects = False
        browser.open(library=LIB_REQUESTS)
        self.assertEqual('Zope', browser.headers['Server'], 'Unscrubbed server version found in the response headers!')

    @browsing
    def test_bobo_call_interface_headers_are_scrubbed_out(self, browser):
        browser.allow_redirects = False
        browser.open(library=LIB_REQUESTS)
        self.assertFalse(
            any(header.lower().startswith('bobo-exception') for header in browser.headers),
            'Bobo-Exception headers found in the response headers!',
        )
