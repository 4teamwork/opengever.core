from ftw.testbrowser import browsing
from opengever.base.error_log import ErrorLogItem
from opengever.base.error_log import get_error_log
from opengever.core.testing import REDIS_INTEGRATION_TESTING
from opengever.testing import IntegrationTestCase
from zExceptions import Unauthorized


class TestErrorLog(IntegrationTestCase):

    layer = REDIS_INTEGRATION_TESTING

    features = ('error_log', )

    @browsing
    def test_list_error_log(self, browser):
        self.login(self.administrator, browser)

        error_item1 = ErrorLogItem(**{'id': 1, 'userid': 'user-a', 'time': 1719323481.488681})
        error_item2 = ErrorLogItem(**{'id': 2, 'userid': 'user-b'})
        error_item3 = ErrorLogItem(**{'id': 3, 'userid': 'user-a'})

        logger = get_error_log()

        logger.push(error_item1)
        logger.push(error_item2)
        logger.push(error_item3)

        browser.open(self.portal.absolute_url() + '/@error-log', headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)

        self.assertEqual({
            u'@id': u'http://nohost/plone/@error-log',
            u'items': [
                {u'id': 3,
                 u'tb_html': u'',
                 u'req_html': u'',
                 u'time': None,
                 u'type': u'',
                 u'userid': u'user-a',
                 u'error': ''},
                {u'id': 2,
                 u'tb_html': u'',
                 u'req_html': u'',
                 u'time': None,
                 u'type': u'',
                 u'userid': u'user-b',
                 u'error': ''},
                {u'id': 1,
                 u'tb_html': u'',
                 u'req_html': u'',
                 u'time': u'2024-06-25T15:51:21.488681',
                 u'type': u'',
                 u'userid': u'user-a',
                 u'error': u''}],
            u'items_total': 3},
            browser.json)

    @browsing
    def test_non_admins_cant_access_the_error_log(self, browser):
        self.login(self.regular_user, browser)
        browser.exception_bubbling = True

        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + '/@error-log', headers=self.api_headers)

    @browsing
    def test_returns_an_empty_list_if_the_feature_is_deactivated(self, browser):
        self.deactivate_feature('error_log')
        self.login(self.administrator, browser)

        error_item1 = ErrorLogItem(**{'id': 1, 'userid': 'user-a'})
        error_item2 = ErrorLogItem(**{'id': 2, 'userid': 'user-b'})
        error_item3 = ErrorLogItem(**{'id': 3, 'userid': 'user-a'})

        logger = get_error_log()

        logger.push(error_item1)
        logger.push(error_item2)
        logger.push(error_item3)

        browser.open(self.portal.absolute_url() + '/@error-log', headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)

        self.assertEqual({
            u'@id': u'http://nohost/plone/@error-log',
            u'items': [],
            u'items_total': 0},
            browser.json)
