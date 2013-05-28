from opengever.testing import OPENGEVER_FUNCTIONAL_TESTING
from plone.testing import layered
import doctest
import unittest2 as unittest


TESTFILES = (
    'localroles.txt',
    'successor.txt',
    'test_overview.txt',
    )


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE |
               doctest.ELLIPSIS |
               doctest.REPORT_NDIFF)


def test_suite():

    suite = unittest.TestSuite()

    for testfile in TESTFILES:
        suite.addTests([
            layered(doctest.DocFileSuite(testfile,
                    optionflags=OPTIONFLAGS),
                    layer=OPENGEVER_FUNCTIONAL_TESTING),
        ])

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
