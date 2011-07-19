import unittest
import os

from Testing import ZopeTestCase as ztc
from opengever.task.tests.layer import Layer
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

import plone.app.dexterity
import opengever.task

@onsetup
def setup_product():

    from opengever.globalindex import Session
    from opengever.globalindex.model import Base
    from z3c.saconfig import EngineFactory
    from z3c.saconfig import GloballyScopedSession
    from z3c.saconfig.interfaces import IEngineFactory
    from z3c.saconfig.interfaces import IScopedSession
    from zope.component import provideUtility

    engine_factory = EngineFactory('sqlite:///:memory:')
    provideUtility(engine_factory, provides=IEngineFactory,
                   name=u'opengever_db')
    scoped_session = GloballyScopedSession(engine=u'opengever_db')
    provideUtility(scoped_session, provides=IScopedSession, name=u'opengever')

    Base.metadata.create_all(Session().bind)

    zcml.load_config('meta.zcml', plone.app.dexterity)
    zcml.load_config('configure.zcml', plone.app.dexterity)
    zcml.load_config('configure.zcml', opengever.task)

setup_product()
ptc.setupPloneSite(extension_profiles=['plone.app.dexterity:default',
                                       'opengever.task:default',
                                       ])

HERE = os.path.dirname( os.path.abspath( __file__ ) )

def test_suite():
    txtfiles = [f for f in os.listdir(HERE)
                if f.endswith('.txt') and
                not f.startswith('.')]
    suites = []
    for f in txtfiles:
        fdfs = ztc.FunctionalDocFileSuite(
                'tests/%s' % f, package='opengever.task',
                test_class=ptc.FunctionalTestCase)
        fdfs.layer = Layer
        suites.append(fdfs)
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
