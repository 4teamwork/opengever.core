from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from zope.configuration import xmlconfig
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class ContactIntegrationLayer(PloneSandboxLayer):
    """Layer for integration tests."""

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        
        # Load testing zcml (optional)
        import opengever.contact
        xmlconfig.file('configure.zcml', opengever.contact, context=configurationContext)
        xmlconfig.file('tests.zcml', opengever.contact, context=configurationContext)
        
    def setUpPloneSite(self, portal):
        applyProfile(portal, 'opengever.contact:default')
        applyProfile(portal, 'opengever.tabbedview:default')
        setRoles(portal, TEST_USER_ID, ['Member', 'Contributor', 'Manager'])


CONTACT_INTEGRATION_FIXTURE = ContactIntegrationLayer()
CONTACT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(CONTACT_INTEGRATION_FIXTURE,), name="Contact:Integration")
CONTACT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(CONTACT_INTEGRATION_FIXTURE,), name="Contact:Functional")

