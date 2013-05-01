#from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
from opengever.base.testing import OPENGEVER_BASE_INTEGRATION_TESTING

import doctest
import unittest2 as unittest
from plone.testing import layered

TESTFILES = (
    'base.txt',
    'classification.txt',
    'copy_item.txt',
    'creator.txt',
    'redirector.txt',
    'reference_adapter.txt',
    'sequence.txt',
    'viewlets.txt',
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
                      layer=OPENGEVER_BASE_INTEGRATION_TESTING),
          ])

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
