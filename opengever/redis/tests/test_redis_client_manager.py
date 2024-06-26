from opengever.core.testing import REDIS_INTEGRATION_TESTING
from opengever.redis.client import redis_client_manager
from opengever.redis.client import RedisClientManager
from opengever.testing import IntegrationTestCase


class TestRedisClientManager(IntegrationTestCase):

    layer = REDIS_INTEGRATION_TESTING

    def test_persists_the_client_for_upcoming_client_requests(self):
        manager = RedisClientManager()
        self.assertEqual(manager.get_client(), manager.get_client())

    def test_can_use_the_client_to_interact_with_redis(self):
        redis_client_manager.get_client().lpush('my_list', 'test-entry')
        self.assertEqual(
            ['test-entry'],
            redis_client_manager.get_client().lrange('my_list', 0, 10))
