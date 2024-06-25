from opengever.base.error_log import DisabledErrorLogRedis
from opengever.base.error_log import ErrorLogItem
from opengever.base.error_log import ErrorLogRedis
from opengever.base.error_log import get_error_log_redis
from opengever.core.testing import REDIS_INTEGRATION_TESTING
from opengever.testing import IntegrationTestCase


class TestErrorLogRedis(IntegrationTestCase):

    layer = REDIS_INTEGRATION_TESTING

    features = ('user_visible_error_logs', )

    def test_can_push_error_log_items(self):
        error_item1 = ErrorLogItem({'id': 1})
        error_item2 = ErrorLogItem({'id': 2})

        logger = get_error_log_redis()
        logger.push(error_item1)
        logger.push(error_item2)

        self.assertEqual([error_item2, error_item1],
                         list(logger.list_all()))

    def test_auto_trim_items_to_max_log_items(self):
        error_item1 = ErrorLogItem({'id': 1})
        error_item2 = ErrorLogItem({'id': 2})
        error_item3 = ErrorLogItem({'id': 3})

        logger = get_error_log_redis()
        logger.MAX_LOG_ITEMS = 2

        logger.push(error_item1)
        logger.push(error_item2)
        logger.push(error_item3)

        self.assertEqual(2, len(list(logger.list_all())))

    def test_sanitizes_html_values(self):
        error_item = ErrorLogItem({'id': 1, 'tb_html': '<p><script>danger</script></p>'})

        logger = get_error_log_redis()
        logger.push(error_item)
        self.assertEqual(u'<p></p>', list(logger.list_all())[0].entry.get('tb_html'))

    def test_can_list_items_by_userid(self):
        error_item1 = ErrorLogItem({'id': 1, 'userid': 'user-a'})
        error_item2 = ErrorLogItem({'id': 2, 'userid': 'user-b'})
        error_item3 = ErrorLogItem({'id': 3, 'userid': 'user-a'})

        logger = get_error_log_redis()

        logger.push(error_item1)
        logger.push(error_item2)
        logger.push(error_item3)

        self.assertEqual([error_item3, error_item1],
                         list(logger.list_all_by_userid('user-a')))

        self.assertEqual([error_item2],
                         list(logger.list_all_by_userid('user-b')))

    def test_error_log_redis_is_feature_flagged(self):
        self.assertIsInstance(get_error_log_redis(), ErrorLogRedis)
        self.deactivate_feature('user_visible_error_logs')
        self.assertIsInstance(get_error_log_redis(), DisabledErrorLogRedis)
