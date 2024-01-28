from sqlalchemy import types
import json


def safe_unicode(value):
    if isinstance(value, str):
        return value.decode('utf-8')
    assert isinstance(value, unicode)
    return value


class UnicodeCoercingText(types.TypeDecorator):
    """TypeDecorator for the `Text` type that always returns unicode for
    values fetched from the DB. This allows us to have a guarantee to always
    receive unicode for `Text` types, even when using Oracle as the backend.

    The effect of this TypeDecorator should be the same as the cxOracle
    dialect option `coerce_to_unicode`, which unfortunately only affects
    `String` columns.
    """

    impl = types.Text
    python_type = unicode

    def process_result_value(self, value, dialect):
        if value is not None:
            value = safe_unicode(value)
        return value


class JSONList(types.TypeDecorator):
    """TypeDecorator to emulate JSON columns for lists.

    Because native JSON columns have only been added in Oracle 21, and
    SQLAlchemy doesn't support them yet (see GH #10375), we emulate them by
    storing data in a Text column, and doing JSON serialization on the way
    in/out in Python.
    """

    impl = types.Text

    def process_bind_param(self, value, dialect):
        assert isinstance(value, (tuple, list, type(None)))
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = tuple(json.loads(value))
        return value
