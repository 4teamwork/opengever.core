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
