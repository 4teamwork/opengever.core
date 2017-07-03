from datetime import datetime
from json import JSONEncoder
from uuid import UUID


class AdvancedJSONEncoder(JSONEncoder):
    """A custom JSONEncoder that can serialize some additional types:

    - datetime -> ISO-format string
    - datetime          -> ISO-format string
    - set      -> list
    - UUID              -> str
    - set               -> list
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj)
        else:
            return super(AdvancedJSONEncoder, self).default(obj)
