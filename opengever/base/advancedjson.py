from datetime import datetime
from dateutil import parser
from opengever.base.date_time import as_utc
from persistent.mapping import PersistentMapping
from uuid import UUID
import json


TYPE_KEY = u'_advancedjson_type'
VALUE_KEY = u'_advancedjson_value'


class CannotDecodeJsonType(Exception):
    """Raised when a decoder receives an unknown type."""

    def __init__(self, unknown_type, unnown_value):
        super(CannotDecodeJsonType, self).__init__(
            "Unknown advanced json type {} and value {}".format(
                unknown_type, unnown_value))
        self.unknown_type = unknown_type
        self.uknown_value = unnown_value


class AdvancedJSONDecoder(json.JSONDecoder):
    """A custom JSONDecoder that can deserialize some additional types.

    Should always be symmetrical in decoding to what AdvancedJSONEncoder
    encodes.
    """

    def __init__(self, *args, **kargs):
        super(AdvancedJSONDecoder, self).__init__(
            *args, object_hook=self._dict_to_object, **kargs)

    def _dict_to_object(self, obj):
        if TYPE_KEY not in obj:
            return obj

        decode_as = obj[TYPE_KEY]
        value = obj[VALUE_KEY]
        if decode_as == u'datetime':
            dt = parser.parse(value)
            if dt.tzinfo:
                dt = as_utc(dt)
            return dt
        elif decode_as == u'UUID':
            return UUID(value)
        elif decode_as == u'set':
            return set(value)
        elif decode_as == u'PersistentMapping':
            return PersistentMapping(value)

        raise CannotDecodeJsonType(decode_as, value)


def load(*args, **kwargs):
    kwargs['cls'] = AdvancedJSONDecoder
    return json.load(*args, **kwargs)


def loads(*args, **kwargs):
    kwargs['cls'] = AdvancedJSONDecoder
    return json.loads(*args, **kwargs)


class AdvancedJSONEncoder(json.JSONEncoder):
    """A custom JSONEncoder that can serialize some additional types.

    The additional types are stored in a custom object/dict with the following
    format:

    {
        u'_advancedjson_type': 'unique identifier',
        u'_advancedjson_value': 'serialized value'
    }
    """

    def encode(self, obj):
        self.ensure_unicode_values(obj)
        return super(AdvancedJSONEncoder, self).encode(obj)

    def ensure_unicode_values(self, obj):
        """Be defensive about encoding issues and only allow unicode strings as
        input value for now.
        """

        if isinstance(obj, str):
            raise ValueError('Expecting unicode value {!r}'.format(obj))
        # it looks like a dict
        # minimal method interface for dict includes keys and __getitem__, so
        # we use those here, according to:
        # https://docs.python.org/2/library/userdict.html#UserDict.DictMixin
        elif hasattr(obj, 'keys'):
            for key in obj.keys():
                self.ensure_unicode_values(obj[key])
        # it looks like an iterable
        elif hasattr(obj, '__iter__'):
            for item in obj:
                self.ensure_unicode_values(item)
        # if it is none of above it is most likely a built-in datatype or
        # something that cannot be encoded in json at all

    def default(self, obj):
        if isinstance(obj, datetime):
            return {
                TYPE_KEY: u'datetime',
                VALUE_KEY: unicode(obj.isoformat()),
            }
        elif isinstance(obj, UUID):
            return {
                TYPE_KEY: u'UUID',
                VALUE_KEY: unicode(obj),
            }
        elif isinstance(obj, set):
            return {
                TYPE_KEY: u'set',
                VALUE_KEY: list(obj),
            }
        elif isinstance(obj, PersistentMapping):
            return {
                TYPE_KEY: u'PersistentMapping',
                VALUE_KEY: dict(obj),
            }
        else:
            return super(AdvancedJSONEncoder, self).default(obj)


def dump(*args, **kwargs):
    kwargs['cls'] = AdvancedJSONEncoder
    return json.dump(*args, **kwargs)


def dumps(*args, **kwargs):
    kwargs['cls'] = AdvancedJSONEncoder
    return json.dumps(*args, **kwargs)
