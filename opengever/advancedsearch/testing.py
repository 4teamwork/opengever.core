from datetime import date
from opengever.globalindex import model as task_model
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.setuphandlers import create_sql_tables, MODELS
from opengever.ogds.base.utils import create_session
from plone.app.testing import applyProfile, IntegrationTesting, \
    PloneSandboxLayer, PLONE_FIXTURE, setRoles, TEST_USER_NAME, \
    TEST_USER_PASSWORD, login
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.configuration import xmlconfig
from opengever.ogds.base.testing import OPENGEVER_OGDS_BASE_FIXTURE
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user

class BaseLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

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
        import opengever.task
        xmlconfig.file('configure.zcml', opengever.task,
                       context=configurationContext)
        import opengever.dossier
        xmlconfig.file('configure.zcml', opengever.dossier,
                        context=configurationContext)
        import opengever.document
        xmlconfig.file('configure.zcml', opengever.document,
                        context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'opengever.contact:default')
        applyProfile(portal, 'opengever.task:default')
        applyProfile(portal, 'opengever.ogds.base:default')
        applyProfile(portal, 'opengever.dossier:default')
        applyProfile(portal, 'opengever.document:default')

        # configure client ID
        registry = getUtility(IRegistry, context=portal)
        client = registry.forInterface(IClientConfiguration)
        client.client_id = u'plone'
        # portal workaround
        self.portal = portal

        # browser tester roles
        setRoles(portal, TEST_USER_NAME, ['Member', 'Contributor', 'Manager'])
        
        login(portal, TEST_USER_NAME)

    def testSetUp(self):
        # setup the sql tables
        create_sql_tables()
        session = create_session()
        session = create_session()
        
        _create_example_client(session, 'plone',
                              {'title': 'Plone',
                              'ip_address': '127.0.0.1',
                              'site_url': 'http://nohost/plone',
                              'public_url': 'http://nohost/plone',
                              'group': 'og_mandant1_users',
                              'inbox_group': 'og_mandant1_inbox'})
        task_model.Base.metadata.create_all(session.bind)

    def testTearDown(test):
        session = create_session()
        for model in MODELS:
            getattr(model, 'metadata').drop_all(session.bind)
        getattr(task_model.Base, 'metadata').drop_all(session.bind)
        # we may have created custom users and


OPENGEVER_ADV_SEARCH_FIXTURE = BaseLayer()
OPENGEVER_ADV_SEARCH_TESTING = IntegrationTesting(
    bases=(OPENGEVER_ADV_SEARCH_FIXTURE,), name="OpengeverAdvancedsearch:Integration")
