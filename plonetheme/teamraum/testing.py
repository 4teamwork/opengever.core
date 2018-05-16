from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_NAME
from zope.configuration import xmlconfig
from opengever.core.testing import clear_transmogrifier_registry


class TeamraumThemeLayer(PloneSandboxLayer):

    defaultBases = (COMPONENT_REGISTRY_ISOLATION, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        clear_transmogrifier_registry()
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

    def setUpPloneSite(self, portal):
        login(portal, TEST_USER_NAME)
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plonetheme.teamraum:default')

    def tearDown(self):
        super(TeamraumThemeLayer, self).tearDown()
        clear_transmogrifier_registry()


TEAMRAUMTHEME_FIXTURE = TeamraumThemeLayer()
TEAMRAUMTHEME_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TEAMRAUMTHEME_FIXTURE,),
    name="plonetheme.teamraum:integration")

TEAMRAUMTHEME_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(TEAMRAUMTHEME_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="plonetheme.teamraum:functional")
