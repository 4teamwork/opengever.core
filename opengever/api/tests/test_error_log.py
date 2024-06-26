from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.error_log import ErrorLogItem
from opengever.base.error_log import get_error_log_redis
from opengever.core.testing import REDIS_INTEGRATION_TESTING
from opengever.testing import IntegrationTestCase
import pytz
import sys


class TestErrorLog(IntegrationTestCase):

    layer = REDIS_INTEGRATION_TESTING

    features = ('user_visible_error_logs', )

    @browsing
    def test_list_error_log(self, browser):
        self.login(self.administrator, browser)

        error_item1 = ErrorLogItem({'id': 1, 'userid': 'user-a', 'time': 1719323481.488681})
        error_item2 = ErrorLogItem({'id': 2, 'userid': 'user-b'})
        error_item3 = ErrorLogItem({'id': 3, 'userid': 'user-a'})

        logger = get_error_log_redis()

        logger.push(error_item1)
        logger.push(error_item2)
        logger.push(error_item3)

        browser.open(self.portal.absolute_url() + '/@error-log', headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)

        self.assertEqual({
            u'@id': u'http://nohost/plone/@error-log',
            u'items': [
                {u'id': 3,
                 u'tb_html': None,
                 u'time': None,
                 u'type': None,
                 u'userid': u'user-a',
                 u'value': None},
                {u'id': 2,
                 u'tb_html': None,
                 u'time': None,
                 u'type': None,
                 u'userid': u'user-b',
                 u'value': None},
                {u'id': 1,
                 u'tb_html': None,
                 u'time': u'2024-06-25T15:51:21.488681',
                 u'type': None,
                 u'userid': u'user-a',
                 u'value': None}],
            u'items_total': 3,
            u'restricted_by_current_user': False},
            browser.json)

    @browsing
    def test_list_error_log_for_restricted_users(self, browser):
        self.login(self.regular_user, browser)

        error_item1 = ErrorLogItem({'id': 1, 'userid': self.regular_user.getId()})
        error_item2 = ErrorLogItem({'id': 2, 'userid': 'user-b'})
        error_item3 = ErrorLogItem({'id': 3, 'userid': self.regular_user.getId()})

        logger = get_error_log_redis()

        logger.push(error_item1)
        logger.push(error_item2)
        logger.push(error_item3)

        browser.open(self.portal.absolute_url() + '/@error-log', headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)

        self.assertEqual({
            u'@id': u'http://nohost/plone/@error-log',
            u'items': [
                {u'id': 3,
                 u'tb_html': None,
                 u'time': None,
                 u'type': None,
                 u'userid': self.regular_user.getId(),
                 u'value': None},
                {u'id': 1,
                 u'tb_html': None,
                 u'time': None,
                 u'type': None,
                 u'userid': self.regular_user.getId(),
                 u'value': None}],
            u'items_total': 2,
            u'restricted_by_current_user': True},
            browser.json)

    @browsing
    def test_returns_an_empty_list_if_the_feature_is_deactivated(self, browser):
        self.deactivate_feature('user_visible_error_logs')
        self.login(self.administrator, browser)

        error_item1 = ErrorLogItem({'id': 1, 'userid': 'user-a'})
        error_item2 = ErrorLogItem({'id': 2, 'userid': 'user-b'})
        error_item3 = ErrorLogItem({'id': 3, 'userid': 'user-a'})

        logger = get_error_log_redis()

        logger.push(error_item1)
        logger.push(error_item2)
        logger.push(error_item3)

        browser.open(self.portal.absolute_url() + '/@error-log', headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)

        self.assertEqual({
            u'@id': u'http://nohost/plone/@error-log',
            u'items': [],
            u'items_total': 0,
            u'restricted_by_current_user': False},
            browser.json)

    @browsing
    def test_site_error_log_properly_logs_errors(self, browser):
        self.login(self.administrator, browser)

        # Raise an error and log it to the SiteErrorLog
        try:
            raise AttributeError("My Dummy Error")
        except AttributeError:
            info = sys.exc_info()

        with freeze(datetime(2018, 11, 22, 14, 29, 33, tzinfo=pytz.UTC)):
            self.portal.error_log.raising(info)

        browser.open(self.portal.absolute_url() + '/@error-log', headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)

        item = browser.json.get('items')[0]
        self.assertEqual(
            {u'@id': u'http://nohost/plone/@error-log',
                u'items': [
                    {
                        u'id': item.get('id'),
                        u'tb_html': item.get('tb_html'),
                        u'time': u'2018-11-22T15:29:33',
                        u'type': u'AttributeError',
                        u'userid': u'nicole.kohler',
                        u'value': u'My Dummy Error'
                    }
                ],
                u'items_total': 1,
                u'restricted_by_current_user': False
            },
            browser.json)
