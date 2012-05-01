from opengever.globalindex import model as task_model
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.setuphandlers import create_sql_tables, MODELS
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.utils import create_session
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.configuration import xmlconfig


class DossierFunctionalLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # do not install pas plugins (doesnt work in tests)
        from opengever.ogds.base import setuphandlers
        setuphandlers.setup_scriptable_plugin = lambda *a, **kw: None

        from opengever.dossier import tests
        xmlconfig.file('testing.zcml', package=tests,
            context=configurationContext)

    def setUpPloneSite(self, portal):

        # Install the example.conference product
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'opengever.ogds.base:default')
        applyProfile(portal, 'opengever.dossier:default')
        applyProfile(portal, 'opengever.document:default')
        applyProfile(portal, 'opengever.task:default')
        applyProfile(portal, 'opengever.tasktemplates:default')
        applyProfile(portal, 'opengever.mail:default')
        applyProfile(portal, 'opengever.tabbedview:default')
        applyProfile(portal, 'opengever.repository:default')

        # setup the sql tables
        create_sql_tables()
        session = create_session()
        task_model.Base.metadata.create_all(session.bind)

        _create_example_client(
            session, 'client1',
            {'title': 'Client 1',
             'ip_address': '127.0.0.1',
             'site_url': 'http://nohost/client1',
             'public_url': 'http://nohost/client1',
             'group': 'client1_users',
             'inbox_group': 'client1_inbox_users'})

        _create_example_user(
            session, portal,
            SITE_OWNER_NAME,
            {'firstname': 'Test',
             'lastname': 'User',
             'email': 'test.user@local.ch',
             'email2': 'test_user@private.ch'},
            ('client1_users',
            'client1_inbox_users'))

        # savepoint "support" for sqlite
        # We need savepoint support for version retrieval with CMFEditions.
        import zope.sqlalchemy.datamanager
        zope.sqlalchemy.datamanager.NO_SAVEPOINT_SUPPORT = set([])

        # configure client ID
        registry = getUtility(IRegistry, context=portal)
        client = registry.forInterface(IClientConfiguration)
        client.client_id = u'client1'

        from plone.app.testing import setRoles, TEST_USER_ID
        setRoles(portal, TEST_USER_ID, ['Member', 'Contributor', 'Editor'])

        # Disable the prevent_deletion subscriber. In tests, we WANT
        # to be able to quickly delete objs without becoming Manager
        from opengever.base import subscribers
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.unregisterHandler(subscribers.prevent_deletion)

    def tearDownPloneSite(self, portal):
        session = create_session()
        for model in MODELS:
            getattr(model, 'metadata').drop_all(session.bind)
        getattr(task_model.Base, 'metadata').drop_all(session.bind)

OPENGEVER_DOSSIER_FIXTURE = DossierFunctionalLayer()
OPENGEVER_DOSSIER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_DOSSIER_FIXTURE, ), name="OpengeverDossier:Integration")
