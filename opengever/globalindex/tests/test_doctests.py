import unittest
import doctest


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)

def setUp(test):
    # setup a sqlite db in memory
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from opengever.globalindex.model import Base
    from opengever.globalindex.model.task import Task
    Task #make pyflakes happy
    engine = create_engine('sqlite:///:memory:', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    # create tables
    Base.metadata.create_all(session.bind)

    test.globs['session'] = session
    
def tearDown(test):
    #test.globs['session'].remove()
    pass

def test_suite():

    return unittest.TestSuite([

        doctest.DocFileSuite(
            'task.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=OPTIONFLAGS),

        doctest.DocFileSuite(
            'query.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=OPTIONFLAGS),

    ])
