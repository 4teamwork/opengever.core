from Products.PloneTestCase import ptc
from Testing import ZopeTestCase
from opengever.document.tests import layer
import doctest
import unittest


MODULENAMES = ()


TESTFILES = (
    'document_id.txt',
    'document_indexers.txt',
    'copy_document.txt',
    'checkout.txt',
    )


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE |
               doctest.ELLIPSIS |
               doctest.REPORT_NDIFF)


def test_suite():

    suite = unittest.TestSuite()

    for testfile in TESTFILES:
        fdfs = ZopeTestCase.FunctionalDocFileSuite(
            testfile,
            optionflags=OPTIONFLAGS,
            test_class=ptc.FunctionalTestCase,)
        fdfs.layer = layer.IntegrationTestLayer
        suite.addTest(fdfs)

    for module in MODULENAMES:
        fdts = ZopeTestCase.FunctionalDocTestSuite(
            module,
            optionflags=OPTIONFLAGS,
            test_class=ptc.FunctionalTestCase)
        fdts.layer = layer.layer
        suite.addTest(fdts)

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
