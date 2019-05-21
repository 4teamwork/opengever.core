from sqlalchemy import exc
from sqlalchemy.event import listen
from sqlalchemy.pool import Pool
from zope.component.hooks import getSite


def alter_session_on_connect(dbapi_connection, connection_record):
    """perform connect operations"""

    cursor = dbapi_connection.cursor()
    cursor.execute('alter session set NLS_SORT=GERMAN_CI')
    cursor.execute('alter session set NLS_COMP=LINGUISTIC')


def setup_isolation_level_on_connect(dbapi_connection, connection_record):
    # This is needed to make (releasing) savepoints work properly with
    # SQLite (needed in tests, particularly opengever.inbox).
    # See http://stackoverflow.com/questions/2036378/
    # using-savepoints-in-python-sqlite3

    dbapi_connection.isolation_level = None


def set_sql_connection_to_readonly_on_begin(conn):
    # Only tested for PostgreSQL
    conn.execute("SET TRANSACTION READ ONLY")


def make_like_case_sensitive(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA case_sensitive_like = ON')


def ping_connection(dbapi_connection, connection_record, connection_proxy):
    # Invalidate stale database connections checked out from the pool
    # Helps us deal with "MySQL has gone away" error
    # See:
    # http://docs.sqlalchemy.org/en/rel_0_7/core/pooling.html#disconnect-handling-pessimistic
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except exc.SQLAlchemyError:
        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()


def setup_engine_options(event):
    """Setup engine / connection options.
        - collation for ORACLE engines
        - transaction isolation level for SQLite engines
    """
    engine = event.engine

    site = getSite()
    conn = site._p_jar
    if conn.isReadOnly():
        listen(engine, 'begin', set_sql_connection_to_readonly_on_begin)

    if engine.name == 'oracle':
        listen(engine, 'connect', alter_session_on_connect)

        # Make sure we always get unicode from SQLAlchemy for columns values.
        # Necessary for SQLAlchemy >= 0.9.2. See:
        # http://docs.sqlalchemy.org/en/latest/dialects/oracle.html#unicode
        if hasattr(engine.dialect, 'coerce_to_unicode'):
            engine.dialect.coerce_to_unicode = True

    elif engine.name == 'sqlite':
        listen(engine, 'connect', setup_isolation_level_on_connect)
        listen(engine, 'connect', make_like_case_sensitive)

    elif engine.name == 'mysql':
        listen(Pool, 'checkout', ping_connection)
