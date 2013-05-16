from opengever.globalindex.testing import MEMORY_DB_LAYER
from plone.testing import layered
import doctest
import unittest


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE |
               doctest.ELLIPSIS |
               doctest.REPORT_NDIFF)

TESTFILES = (
    'task.txt',
    'task_principals.txt',
    )


def test_suite():

    suite = unittest.TestSuite()

    for testfile in TESTFILES:
        suite.addTests([
                layered(doctest.DocFileSuite(
                        testfile, optionflags=OPTIONFLAGS),
                        layer=MEMORY_DB_LAYER),
                ])
    return suite
