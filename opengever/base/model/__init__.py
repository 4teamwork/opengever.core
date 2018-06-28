from opengever.base.interfaces import ISQLFormSupport
from opengever.ogds.models import BASE
from opengever.ogds.models.declarative import query_base
from plone import api
from plone.api.exc import CannotGetPortalError
from sqlalchemy import types
from sqlalchemy_i18n import make_translatable
from z3c.saconfig import named_scoped_session
from zope.interface import implements
import pytz
import sqlalchemy_utils

DEFAULT_LOCALE = 'de'
SUPPORTED_LOCALES = ['de', 'fr', 'en']


CONTENT_TITLE_LENGTH = 255
PORTAL_TYPE_LENGTH = 100
ZIP_CODE_LENGTH = 16
CSS_CLASS_LENGTH = 100
UID_LENGTH = 36


tables = [
    'favorites',
]


def get_locale():
    try:
        ltool = api.portal.get_tool('portal_languages')
    except CannotGetPortalError:
        return DEFAULT_LOCALE

    language_code = ltool.getPreferredLanguage()
    return language_code.split('-')[0]


Session = named_scoped_session('opengever')

BASE.session = Session
Base = query_base(Session)

make_translatable(options={'locales': SUPPORTED_LOCALES})
sqlalchemy_utils.i18n.get_locale = get_locale


def get_tables(table_names):
    tables = Base.metadata.tables
    return [tables.get(table_name) for table_name in table_names]


def create_session():
    """Returns a new sql session bound to the defined named scope.
    """
    return Session()


def is_oracle():
    """Returns a new sql session bound to the defined named scope.
    """
    return 'oracle' in create_session().connection().dialect.name


class UTCDateTime(types.TypeDecorator):
    """Sqlalchemy does not support timezone aware datetimes for Sqlite and
    MySQL backend. Therefore we have to ensure that timezone aware datetimes
    are returned.
    """

    impl = types.DateTime

    def process_bind_param(self, value, engine):
        if value is not None:
            return value.astimezone(pytz.UTC)

    def process_result_value(self, value, engine):
        if value is not None:
            if value.tzinfo is None:
                # We manually add the UTC timezone, only needed for the DB
                # backend who does not support timezone aware datetime.
                value = pytz.UTC.localize(value)
            return value


class SQLFormSupport(object):
    implements(ISQLFormSupport)

    def is_editable(self):
        return True

    def is_editable_by_current_user(self, container):
        return api.user.has_permission('Modify portal content', obj=container)

    def get_edit_url(self, context):
        return self.get_url(context, view='edit')

    def get_edit_values(self, fieldnames):
        _marker = object()

        values = {}
        for fieldname in fieldnames:
            value = getattr(self, fieldname, _marker)
            if value is _marker:
                continue

            values[fieldname] = value
        return values

    def update_model(self, data):
        for key, value in data.items():
            setattr(self, key, value)
