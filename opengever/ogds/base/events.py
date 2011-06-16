from opengever.ogds.base.utils import create_session

def setup_oracle_collation(event):
    """Setup collation for oracle engines.
    """
    engine = event.engine
    if engine.name == 'oracle':
        engine.execute('alter session set NLS_SORT=BINARY_CI')
        engine.execute('alter session set NLS_COMP=LINGUISTIC')

    session = create_session()
    if session.bind.name == 'oracle':
        session.bind.execute('alter session set NLS_SORT=BINARY_CI')
        session.bind.execute('alter session set NLS_COMP=LINGUISTIC')
