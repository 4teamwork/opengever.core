from sqlalchemy import types


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
