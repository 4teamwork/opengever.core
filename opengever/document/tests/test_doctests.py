import unittest2 as unittest
import doctest
from plone.testing import layered
from opengever.document.testing import OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING


TESTFILES = (
    'document_id.txt',
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
                    layer=OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING),
        ])

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
