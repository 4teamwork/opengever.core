from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, TEST_USER_ID, setRoles
from zope.configuration import xmlconfig


class TrashLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):

        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'

            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'

            '  <include package="opengever.ogds.base" file="tests.zcml" />'

            '</configure>',
            context=configurationContext)

        import opengever.trash
        xmlconfig.file('tests.zcml',
                       opengever.trash, context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'opengever.trash:default')
        setRoles(portal, TEST_USER_ID, ['Member', 'Contributor', 'Manager'])
        # portal workaround
        self.portal = portal

OPENGEVER_TRASH_FIXTURE = TrashLayer()
OPENGEVER_TRASH_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_TRASH_FIXTURE,), name="OpengeverTrash:Integration")
