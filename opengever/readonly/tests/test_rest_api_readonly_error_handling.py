from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode


class TestRESTAPIReadOnlyErrorHandling(FunctionalTestCase):

    @browsing
    def test_read_only_error_is_properly_serialized(self, browser):
        browser.login()

        with ZODBStorageInReadonlyMode():
            with browser.expect_http_error(code=500):
                browser.open(
                    self.portal,
                    view='@test-write-on-read',
                    headers={
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'},
                )

            self.assertEqual({
                u'message': u'',
                u'type': u'ReadOnlyError'},
                browser.json)
