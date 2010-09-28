from plone.app.testing import IntegrationTesting
from opengever.ogds.base.setuphandlers import create_sql_tables, MODELS
from opengever.ogds.base.utils import create_session
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig
from zope.component import getUtility
from opengever.ogds.base.interfaces import IClientConfiguration
from plone.registry.interfaces import IRegistry


class BaseLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # do not install pas plugins (doesnt work in tests)
        from opengever.ogds.base import setuphandlers
        setuphandlers.setup_scriptable_plugin = lambda *a, **kw: None
        # Load configure.zcml
        import opengever.ogds.base
        xmlconfig.file('configure.zcml', opengever.ogds.base,
                       context=configurationContext)
        xmlconfig.file('tests.zcml', opengever.ogds.base,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'opengever.ogds.base:default')
        # configure client ID
        registry = getUtility(IRegistry, context=portal)
        client = registry.forInterface(IClientConfiguration)
        client.client_id = u'client1'

    def testSetUp(self):
        # setup the sql tables
        create_sql_tables()

    def testTearDown(test):
        session = create_session()
        for model in MODELS:
            getattr(model, 'metadata').drop_all(session.bind)


OPENGEVER_OGDS_BASE_FIXTURE = BaseLayer()
OPENGEVER_OGDS_BASE_TESTING = IntegrationTesting(
    bases=(OPENGEVER_OGDS_BASE_FIXTURE,), name="OpengeverOgdsBase:Integration")
