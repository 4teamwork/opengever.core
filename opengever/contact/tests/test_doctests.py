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



# 
# 
# 
# import unittest
# import doctest
# from Testing import ZopeTestCase as ztc
# from opengever.contact.tests.base import ContactTestCase
# 
# 
# import os
# 
# from Products.Five import zcml
# from Products.PloneTestCase import PloneTestCase as ptc
# from Products.PloneTestCase.layer import onsetup
# 
# import plone.app.dexterity
# import opengever.contact
# 
# OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
#                doctest.ELLIPSIS|
#                doctest.REPORT_NDIFF)
# 
# @onsetup
# def setup_product():
#    zcml.load_config('meta.zcml', plone.app.dexterity)
#    zcml.load_config('configure.zcml', plone.app.dexterity)
#    zcml.load_config('configure.zcml', opengever.contact)
# 
# setup_product()
# ptc.setupPloneSite(extension_profiles=['plone.app.dexterity:default',
#                                       'opengever.contact:default',
#                                       ])

# def test_suite():
#     return unittest.TestSuite([
#         # doctests in file bar.txt
#         ztc.ZopeDocFileSuite(
#             'contact.txt', package='opengever.contact.tests',
#             test_class=ptc.FunctionalTestCase, optionflags=OPTIONFLAGS),
# 
#         # docstring tests for module ftw.foo.bar
#         # ztc.ZopeDocTestSuite(
#         #             'ftw.foo.bar',
#         #              test_class=FooTestCase, optionflags=OPTIONFLAGS),
#     ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

