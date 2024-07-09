from copy import deepcopy
from datetime import datetime
from opengever.base.interfaces import IBaseSettings
from opengever.base.utils import to_safe_html
from opengever.redis.client import redis_client_manager
from plone import api
import json


def is_redis_error_log_feature_enabled():
    return api.portal.get_registry_record(
        'is_redis_error_log_feature_enabled', interface=IBaseSettings)


class RedisErrorLog:
    STORAGE_KEY = 'error_log'
    MAX_LOG_ITEMS = 200

    def __init__(self, redis_client):
        self.client = redis_client

    def push(self, error_log_item):
        if not isinstance(error_log_item, ErrorLogItem):
            raise Exception('Requires an ErrorLogItem')

        self.client.lpush(self.STORAGE_KEY, error_log_item.to_json())
        self.trim()

    def list_all(self):
        for value in self.client.lrange(self.STORAGE_KEY, 0, self.MAX_LOG_ITEMS):
            yield ErrorLogItem.from_json(value)

    def trim(self):
        self.client.ltrim(self.STORAGE_KEY, 0, self.MAX_LOG_ITEMS - 1)

    def clear(self):
        self.client.delete(self.STORAGE_KEY)


class NullErrorLog:
    def __init__(self, *args, **kwargs):
        pass

    def push(self, *args, **kwargs):
        pass

    def list_all(self):
        return []

    def trim(self):
        pass

    def clear(self):
        pass


class ErrorLogItem:
    def __init__(self, *args, **log_data):
        self.entry = {
            'type': log_data.get('type', ''),
            'error': log_data.get('error', ''),
            'time': log_data.get('time', None),
            'id': log_data.get('id', ''),
            'tb_html': to_safe_html(log_data.get('tb_html', '')),
            'req_html': to_safe_html(log_data.get('req_html', '')),
            'userid': log_data.get('userid', '')
        }

    @classmethod
    def from_json(cls, value):
        return ErrorLogItem(**json.loads(value))

    def to_json(self):
        return json.dumps(self.entry)

    @property
    def userid(self):
        return self.entry.get('userid', '')

    def serialize(self):
        entry = deepcopy(self.entry)

        if self.entry.get('time'):
            entry['time'] = datetime.fromtimestamp(self.entry.get('time')).isoformat()

        return entry

    def __eq__(self, other):
        return self.entry == other.entry

    def __repr__(self):
        return "<ErrorLogItem {}>".format(self.entry.get('id', 'missing-id'))


def get_error_log():
    if is_redis_error_log_feature_enabled():
        return RedisErrorLog(redis_client_manager.get_client())
    return NullErrorLog()
