import doctest
from plone.testing import layered
import unittest2 as unittest
from opengever.tabbedview.testing import OPENGEVER_TABBEDVIEW_TESTING


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)


TESTFILES = (
    'helpers.txt',
    )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([layered(doctest.DocFileSuite(filename,
                                                 optionflags=OPTIONFLAGS),
                            layer=OPENGEVER_TABBEDVIEW_TESTING)
                    for filename in TESTFILES])
    return suite
