from redis import Redis
import os


class RedisClientManager:
    client = None

    def _setup_client(self):
        client = Redis.from_url(os.environ.get('REDIS_URL', '').strip('/'))
        self.client = client

    def get_client(self):
        if not self.client:
            self._setup_client()

        return self.client


redis_client_manager = RedisClientManager()
