from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2
from zope.configuration import xmlconfig


class TeamraumThemeLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
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


TEAMRAUMTHEME_FIXTURE = TeamraumThemeLayer()
TEAMRAUMTHEME_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TEAMRAUMTHEME_FIXTURE,),
    name="plonetheme.teamraum:integration")
TEAMRAUMTHEME_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(TEAMRAUMTHEME_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="plonetheme.teamraum:functional")


class TeamraumThemeSubsiteLayer(TeamraumThemeLayer):

    def setUpZope(self, app, configurationContext):

        import ftw.subsite
        xmlconfig.file('configure.zcml', ftw.subsite,
                       context=configurationContext)
        z2.installProduct(app, 'ftw.subsite')

        super(TeamraumThemeSubsiteLayer,
              self).setUpZope(app, configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.subsite:default')

        super(TeamraumThemeSubsiteLayer, self).setUpPloneSite(portal)

TEAMRAUMTHEME_SUBSITE_FIXTURE = TeamraumThemeSubsiteLayer()
THEME_SUBSITE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TEAMRAUMTHEME_SUBSITE_FIXTURE,),
    name="plonetheme.teamraum:subiste-integration")
