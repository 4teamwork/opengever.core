from zope.site.hooks import setHooks
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from zope.configuration import xmlconfig
from five.intid import site


class OpengeverDocumentLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import opengever.document
        xmlconfig.file('configure.zcml', opengever.document,
                       context=configurationContext)
        xmlconfig.file('tests.zcml', opengever.document,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        site.add_intids(portal)
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plone.app.dexterity:default')
        applyProfile(portal, 'opengever.document:default')
        applyProfile(portal, 'opengever.document:tests')
        # set hooks
        setHooks()


OPENGEVER_DOCUMENT_FIXTURE = OpengeverDocumentLayer()
OPENGEVER_DOCUMENT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_DOCUMENT_FIXTURE,), name="OpengeverDocument:Integration")
