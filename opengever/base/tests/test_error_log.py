from opengever.base.error_log import ErrorLogItem
from opengever.base.error_log import get_error_log
from opengever.base.error_log import NullErrorLog
from opengever.base.error_log import RedisErrorLog
from opengever.core.testing import REDIS_INTEGRATION_TESTING
from opengever.testing import IntegrationTestCase


class TestRedisErrorLog(IntegrationTestCase):

    layer = REDIS_INTEGRATION_TESTING

    features = ('error_log', )

    def test_can_push_error_log_items(self):
        error_item1 = ErrorLogItem(**{'id': 1})
        error_item2 = ErrorLogItem(**{'id': 2})

        logger = get_error_log()
        logger.push(error_item1)
        logger.push(error_item2)

        self.assertEqual([error_item2, error_item1],
                         list(logger.list_all()))

    def test_auto_trim_items_to_max_log_items(self):
        error_item1 = ErrorLogItem(**{'id': 1})
        error_item2 = ErrorLogItem(**{'id': 2})
        error_item3 = ErrorLogItem(**{'id': 3})

        logger = get_error_log()
        logger.MAX_LOG_ITEMS = 2

        logger.push(error_item1)
        logger.push(error_item2)
        logger.push(error_item3)

        self.assertEqual(2, len(list(logger.list_all())))

    def test_sanitizes_html_values(self):
        error_item = ErrorLogItem(**{
            'tb_html': '<p><script>danger</script></p>',
            'req_html': '<p><script>danger</script></p>'
        })

        logger = get_error_log()
        logger.push(error_item)
        self.assertEqual(u'<p></p>', list(logger.list_all())[0].entry.get('tb_html'))
        self.assertEqual(u'<p></p>', list(logger.list_all())[0].entry.get('req_html'))

    def test_error_log_redis_is_feature_flagged(self):
        self.assertIsInstance(get_error_log(), RedisErrorLog)
        self.deactivate_feature('error_log')
        self.assertIsInstance(get_error_log(), NullErrorLog)
