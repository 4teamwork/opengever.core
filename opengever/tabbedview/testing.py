from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from zope.configuration import xmlconfig


class BaseLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'

            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'

            '  <include package="opengever.ogds.base" file="tests.zcml" />'

            '</configure>',
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
