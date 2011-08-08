import doctest
import unittest
from zope.testing import doctestunit
from zope.app.testing import setup

def setUp(test):
    pass

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    return unittest.TestSuite((
        doctestunit.DocFileSuite(
            '../behaviors.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
        #
        # import doctest
        # from zope.app.testing import setup
        # from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
        # import unittest2 as unittest
        # from plone.testing import layered
        #
        # TESTFILES = (
        #     '../behaviors.txt',
        #     )
        #
        #
        # def setUp(test):
        #     pass
        #
        # def tearDown(test):
        #     setup.placefulTearDown()
        #
        # def test_suite():
        #
        #     suite = unittest.TestSuite()
        #
        #     for testfile in TESTFILES:
        #         suite.addTests([
        #               layered(doctest.DocFileSuite(testfile),
        #                       layer=OPENGEVER_DOSSIER_INTEGRATION_TESTING),
        #           ])
        #
        #     return suite