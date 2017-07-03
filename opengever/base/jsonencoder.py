from datetime import datetime
from json import JSONEncoder
from persistent.mapping import PersistentMapping
from uuid import UUID


class AdvancedJSONEncoder(JSONEncoder):
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
