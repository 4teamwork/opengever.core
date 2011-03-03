def setup_oracle_collation(event):
    """Setup collation for oracle engines.
    """
    engine = event.engine
    if engine.name == 'oracle':
        engine.execute('alter session set NLS_SORT=BINARY_CI')
        engine.execute('alter session set NLS_COMP=LINGUISTIC')
