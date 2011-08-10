import doctest
import unittest2 as unittest
from plone.testing import layered
from opengever.inbox.testing import OPENGEVER_INBOX_INTEGRATION_TESTING

TESTFILES = (
    'forwarding.txt',
    'views.txt',
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
                        layer=OPENGEVER_INBOX_INTEGRATION_TESTING),
            ])

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
