# the sqlalchemy 0.7 way:
# from sqlalchemy import events
from sqlalchemy.interfaces import PoolListener

# the sqlalchemy 0.7 way:
# def alter_session_on_connect(dbapi_connection, connection_record):
#     """
#     """
#     dbapi_connection.execute('alter session set NLS_SORT=GERMAN_CI')
#     dbapi_connection.execute('alter session set NLS_COMP=LINGUISTIC')


class SetupCollationListener(PoolListener):

    def connect(self, dbapi_con, con_record):
        '''perform connect operations'''
        cursor = dbapi_con.cursor()
        cursor.execute('alter session set NLS_SORT=GERMANY_CI')
        cursor.execute('alter session set NLS_COMP=LINGUISTIC')


class SetupIsolationLevelListener(PoolListener):

    def connect(self, dbapi_con, con_record):
        '''perform connect operations'''
        # This is needed to make (releasing) savepoints work properly with
        # SQLite (needed in tests, particularly opengever.inbox).
        # See http://stackoverflow.com/questions/2036378/using-savepoints-in-python-sqlite3
        dbapi_con.isolation_level = None


def setup_engine_options(event):
    """Setup engine / connection options.
        - collation for ORACLE engines
        - transaction isolation level for SQLite engines
    """
    engine = event.engine
    if engine.name == 'oracle':
        engine.pool.add_listener(SetupCollationListener())
        # the sqlalchemy 0.7 way:
        #events.listen(engine, 'connect', alter_session_on_connect)
    elif engine.name == 'sqlite':
        engine.pool.add_listener(SetupIsolationLevelListener())
