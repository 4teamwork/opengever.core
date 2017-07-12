from datetime import datetime
from dateutil import parser
from opengever.base.date_time import as_utc
from persistent.mapping import PersistentMapping
from uuid import UUID
import json


class AdvancedJSONDecoder(json.JSONDecoder):
    """A custom JSONDecoder that can deserialize some additional types:

    - ISO-format string -> datetime
    """

    def __init__(self, *args, **kargs):
        super(AdvancedJSONDecoder, self).__init__(
            *args, object_hook=self._dict_to_object, **kargs)

    def _dict_to_object(self, obj):
        for key, val in obj.items():
            if not isinstance(val, basestring):
                continue
            try:
                dt = parser.parse(val)
            except ValueError:
                continue
            else:
                if dt.tzinfo:
                    dt = as_utc(dt)
                obj[key] = dt
        return obj


def load(*args, **kwargs):
    kwargs['cls'] = AdvancedJSONDecoder
    return json.load(*args, **kwargs)


def loads(*args, **kwargs):
    kwargs['cls'] = AdvancedJSONDecoder
    return json.loads(*args, **kwargs)


class AdvancedJSONEncoder(json.JSONEncoder):
    """A custom JSONEncoder that can serialize some additional types:

    - datetime          -> ISO-format string
    - UUID              -> str
    - PersistentMapping -> dict
    - set               -> list
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, PersistentMapping):
            return dict(obj)
        else:
            return super(AdvancedJSONEncoder, self).default(obj)


def dump(*args, **kwargs):
    kwargs['cls'] = AdvancedJSONEncoder
    return json.dump(*args, **kwargs)


def dumps(*args, **kwargs):
    kwargs['cls'] = AdvancedJSONEncoder
    return json.dumps(*args, **kwargs)
