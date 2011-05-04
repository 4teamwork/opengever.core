from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from zope.configuration import xmlconfig


class BaseLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load configure.zcml
        import opengever.tabbedview
        xmlconfig.file('configure.zcml', opengever.tabbedview,
                       context=configurationContext)
        xmlconfig.file('tests.zcml', opengever.tabbedview,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'opengever.tabbedview:default')

    def testSetUp(self):
        pass

    def testTearDown(test):
        pass


OPENGEVER_TABBEDVIEW_FIXTURE = BaseLayer()
OPENGEVER_TABBEDVIEW_TESTING = IntegrationTesting(
    bases=(OPENGEVER_TABBEDVIEW_FIXTURE,),
    name="OpengeverTabbedview:Integration")
