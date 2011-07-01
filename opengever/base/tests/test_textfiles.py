import unittest
import os

from Testing import ZopeTestCase as ztc

from opengever.base.tests.base import OpengeverBaseTestCase

HERE = os.path.dirname( os.path.abspath( __file__ ) )

def test_suite():
    txtfiles = [f for f in os.listdir(HERE)
                if f.endswith('.txt') and
                not f.startswith('.')]
    return unittest.TestSuite(
        [ztc.FunctionalDocFileSuite(
                'tests/%s' % f, package='opengever.base',
                test_class=OpengeverBaseTestCase)
         for f in txtfiles]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
