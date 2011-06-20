import unittest
import os

from Testing import ZopeTestCase as ztc

from opengever.repository.tests.base import OpengeverRepositoryTestCase

HERE = os.path.dirname( os.path.abspath( __file__ ) )

def test_suite():
    txtfiles = [f for f in os.listdir(HERE)
                if f.endswith('.txt') and
                not f.startswith('.')]
    return unittest.TestSuite(
        [ztc.FunctionalDocFileSuite(
                'tests/%s' % f, package='opengever.repository',
                test_class=OpengeverRepositoryTestCase)
         for f in txtfiles]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
    
