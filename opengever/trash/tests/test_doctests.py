import doctest
from plone.testing import layered
import unittest2 as unittest
from opengever.trash.testing import OPENGEVER_TRASH_INTEGRATION_TESTING


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)


TESTFILES = (
    'trash.txt',
    )



def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([layered(doctest.DocFileSuite(filename,
                                                 optionflags=OPTIONFLAGS),
                    layer=OPENGEVER_TRASH_INTEGRATION_TESTING)
                    for filename in TESTFILES])
    return suite
