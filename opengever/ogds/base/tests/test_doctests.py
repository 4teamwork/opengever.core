import doctest
from plone.testing import layered
import unittest2 as unittest
from opengever.ogds.base.testing import OPENGEVER_OGDS_BASE_TESTING


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)


TESTFILES = (
    'user_model.txt',
    'client_model.txt',
    'contact_info.txt',
    'vocabularies.txt',
    )



def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([layered(doctest.DocFileSuite(filename,
                                                 optionflags=OPTIONFLAGS),
                    layer=OPENGEVER_OGDS_BASE_TESTING)
                    for filename in TESTFILES])
    return suite
