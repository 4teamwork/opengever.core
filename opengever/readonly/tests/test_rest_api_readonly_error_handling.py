from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode
import json


class TestRESTAPIReadOnlyErrorHandling(FunctionalTestCase):

    @browsing
    def test_read_only_error_is_properly_serialized(self, browser):
        browser.login()

        with ZODBStorageInReadonlyMode():
            with browser.expect_http_error(code=500):
                browser.open(
                    self.portal, method='POST',
                    headers={
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'},
                    data=json.dumps({
                        '@type': 'opengever.document.document',
                        'title': 'foo'})
                )
            self.assertEqual({
                u'message': u'',
                u'type': u'ReadOnlyError'},
                browser.json)
