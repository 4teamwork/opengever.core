from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.testing import FunctionalSplinterTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import applyProfile
from plone.app.testing import login
from zope.configuration import xmlconfig


class GeverThemeLayer(PloneSandboxLayer):

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
        applyProfile(portal, 'opengever.theme:default')


GEVERTHEME_FIXTURE = GeverThemeLayer()
GEVERTHEME_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GEVERTHEME_FIXTURE,),
    name="opengever.theme:integration")
GEVERTHEME_FUNCTIONAL_TESTING = FunctionalSplinterTesting(
    bases=(GEVERTHEME_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="opengever.theme:functional")
