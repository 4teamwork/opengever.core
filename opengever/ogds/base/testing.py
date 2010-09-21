from plone.app.testing import IntegrationTesting
from opengever.ogds.base.setuphandlers import create_sql_tables, MODELS
from opengever.ogds.base.utils import create_session
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


class BaseLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load configure.zcml
        import opengever.ogds.base
        xmlconfig.file('configure.zcml', opengever.ogds.base)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'opengever.ogds.base:default')

    def setUp(self):
        # Load test.zcml with database configuration
        import opengever.ogds.base
        xmlconfig.file('test.zcml', opengever.ogds.base)

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
