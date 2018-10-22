from pyxb.binding.datatypes import date as pyxb_date
import dateutil.parser
import json


ECH_0147_DATE_FIELDS = ('start', 'document_date')
ECH_0147_DATETIME_FIELDS = ()


class ECH0147Serializer(json.JSONEncoder):
    """Sanitize inputs for eCH-0147 imports via JSON serialization."""

    def default(self, obj):
        if isinstance(obj, pyxb_date):
            return obj.isoformat()
        return obj

    def decode(self, string):
        """We only get flat enough dicts to know dates are on the top level."""
        obj = json.loads(string)

        for key, value in obj.items():
            if isinstance(value, basestring):
                if key in ECH_0147_DATE_FIELDS:
                    obj[key] = dateutil.parser.parse(value).date()
                elif key in ECH_0147_DATETIME_FIELDS:
                    obj[key] = dateutil.parser.parse(value)
                else:
                    pass

        return obj
