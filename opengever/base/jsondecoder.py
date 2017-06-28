from dateutil import parser
from json import JSONDecoder
from opengever.base.date_time import as_utc


class AdvancedJSONDecoder(JSONDecoder):
    """A custom JSONEncoder that can deserialize some additional types:

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
