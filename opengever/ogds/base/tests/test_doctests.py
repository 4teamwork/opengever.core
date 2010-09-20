from opengever.ogds.base.setuphandlers import create_sql_tables, MODELS
from opengever.ogds.base.utils import create_session
from zope.configuration import xmlconfig
import doctest
import unittest2 as unittest


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)


TESTFILES = (
    'user_model.txt',
    'client_model.txt',
    'contact_info.txt',
    )


def setUp(test):
    # Load test.zcml
    import opengever.ogds.base
    xmlconfig.file('test.zcml', opengever.ogds.base)
    # setup the sql tables
    create_sql_tables()
    # provide a session
    test.globs['session'] = create_session()


def tearDown(test):
    session = create_session()
    for model in MODELS:
        getattr(model, 'metadata').drop_all(session.bind)


def test_suite():
    suite = unittest.TestSuite()
    for testfile in TESTFILES:
        suite.addTest(doctest.DocFileSuite(
                testfile,
                setUp=setUp, tearDown=tearDown,
                optionflags=OPTIONFLAGS))
    return suite
