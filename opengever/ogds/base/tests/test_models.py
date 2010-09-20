import unittest
import doctest


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)




def setUp(test):
    # setup a sqlite db in memory
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('sqlite:///:memory:', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    test.globs['session'] = session

    # create tables
    from opengever.ogds.base.model.client import Client
    from opengever.ogds.base.model.user import User

    Client.metadata.create_all(session.bind)
    User.metadata.create_all(session.bind)


def tearDown(test):
    pass


def test_suite():

    return unittest.TestSuite([

            doctest.DocFileSuite(
                'user_model.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=OPTIONFLAGS),

            doctest.DocFileSuite(
                'client_model.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=OPTIONFLAGS),

            ])
