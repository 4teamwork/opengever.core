from opengever.testing import OPENGEVER_FUNCTIONAL_TESTING
from plone.testing import layered
import doctest
import os
import unittest2 as unittest


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)


HERE = os.path.dirname(os.path.abspath(__file__))


def test_suite():

    suite = unittest.TestSuite()

    txtfiles = [f for f in os.listdir(HERE)
                if f.endswith('.txt') and
                not f.startswith('.')]


    for testfile in txtfiles:
            suite.addTests([
                  layered(doctest.DocFileSuite(testfile,
                                               optionflags=OPTIONFLAGS),
                          layer=OPENGEVER_FUNCTIONAL_TESTING),
              ])

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
