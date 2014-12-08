from sqlalchemy import exc
from sqlalchemy.event import listen
from sqlalchemy.pool import Pool


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


def ping_connection(dbapi_connection, connection_record, connection_proxy):
    # Invalidate stale database connections checked out from the pool
    # Helps us deal with "MySQL has gone away" error
    # See:
    # http://docs.sqlalchemy.org/en/rel_0_7/core/pooling.html#disconnect-handling-pessimistic
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
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
    if engine.name == 'oracle':
        # the sqlalchemy 0.7 way:
        listen(engine, 'connect', alter_session_on_connect)

    elif engine.name == 'sqlite':
        listen(engine, 'connect', setup_isolation_level_on_connect)

    elif engine.name == 'mysql':
        listen(Pool, 'checkout', ping_connection)
