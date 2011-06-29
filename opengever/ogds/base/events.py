# the sqlalchemy 0.7 way:
# from sqlalchemy import events
from sqlalchemy.interfaces import PoolListener

# the sqlalchemy 0.7 way:
# def alter_session_on_connect(dbapi_connection, connection_record):
#     """
#     """
#     dbapi_connection.execute('alter session set NLS_SORT=BINARY_CI')
#     dbapi_connection.execute('alter session set NLS_COMP=LINGUISTIC')


class SetupCollationListener(PoolListener):

    def connect(self, dbapi_con, con_record):
        '''perform connect operations'''
        cursor = dbapi_con.cursor()
        cursor.execute('alter session set NLS_SORT=BINARY_CI')
        cursor.execute('alter session set NLS_COMP=LINGUISTIC')

def setup_oracle_collation(event):
    """Setup collation for oracle engines.
    """
    engine = event.engine
    if engine.name == 'oracle':
        engine.pool.add_listener(SetupCollationListener())
        # the sqlalchemy 0.7 way:
        #events.listen(engine, 'connect', alter_session_on_connect)
