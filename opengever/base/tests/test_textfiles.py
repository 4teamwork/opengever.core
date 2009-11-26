import unittest
import os

from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

import plone.app.dexterity
import opengever.base

@onsetup
def setup_product():
    zcml.load_config('meta.zcml', plone.app.dexterity)
    zcml.load_config('configure.zcml', plone.app.dexterity)
    zcml.load_config('configure.zcml', opengever.base)

setup_product()
ptc.setupPloneSite(extension_profiles=['plone.app.dexterity:default',
                                       #'opengever.base:default',
                                       ])

HERE = os.path.dirname( os.path.abspath( __file__ ) )

def test_suite():
    txtfiles = [f for f in os.listdir(HERE)
                if f.endswith('.txt') and
                not f.startswith('.')]
    return unittest.TestSuite(
        [ztc.FunctionalDocFileSuite(
                'tests/%s' % f, package='opengever.base',
                test_class=ptc.FunctionalTestCase)
         for f in txtfiles]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
