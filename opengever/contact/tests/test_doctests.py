from opengever.contact.testing import CONTACT_FUNCTIONAL_TESTING
from Products.Five import zcml
import unittest2 as unittest
import opengever.contact
import doctest
from plone.testing import layered
OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF|
               doctest.REPORT_ONLY_FIRST_FAILURE)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite('contact.txt', optionflags=OPTIONFLAGS),
                layer=CONTACT_FUNCTIONAL_TESTING),
    ])
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

