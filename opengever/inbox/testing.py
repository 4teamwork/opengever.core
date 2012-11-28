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
from plone.app.testing.interfaces import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.configuration import xmlconfig


class InboxFunctionalLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # do not install pas plugins (doesnt work in tests)
         from opengever.ogds.base import setuphandlers
         setuphandlers.setup_scriptable_plugin = lambda *a, **kw: None

         import ftw.contentmenu
         xmlconfig.file('configure.zcml', package=ftw.contentmenu,
             context=configurationContext)

         from opengever.inbox import tests
         xmlconfig.file('testing.zcml', package=tests,
             context=configurationContext)

    def setUpPloneSite(self, portal):

        applyProfile(portal, 'opengever.inbox:default')
        applyProfile(portal, 'opengever.document:default')
        applyProfile(portal, 'opengever.task:default')
        applyProfile(portal, 'ftw.contentmenu:default')

        # setup the sql tables
        create_sql_tables()
        session = create_session()
        task_model.Base.metadata.create_all(session.bind)

        _create_example_client(session, 'plone',
                              {'title': 'plone',
                              'ip_address': '127.0.0.1',
                              'site_url': 'http://nohost/plone',
                              'public_url': 'http://nohost/plone',
                              'group': 'og_mandant1_users',
                              'inbox_group': 'og_mandant1_inbox'})

        _create_example_client(session, 'client2',
                            {'title': 'client2',
                            'ip_address': '127.0.0.1',
                            'site_url': 'http://nohost/plone',
                            'public_url': 'http://nohost/plone',
                            'group': 'og_mandant2_users',
                            'inbox_group': 'og_mandant2_inbox'})

        _create_example_user(
            session, portal,
            TEST_USER_ID,
            {'firstname': 'Test',
             'lastname': 'User',
             'email': 'test.user@local.ch',
             'email2': 'test_user@private.ch'},
             ('og_mandant1_users','og_mandant1_inbox'))

        # configure client ID
        registry = getUtility(IRegistry, context=portal)
        client = registry.forInterface(IClientConfiguration)
        client.client_id = u'plone'
        #
        # setRoles(portal, TEST_USER_ID, ['Member', 'Contributor', 'Editor'])

        # savepoint "support" for sqlite
        # We need savepoint support for version retrieval with CMFEditions.
        import zope.sqlalchemy.datamanager
        zope.sqlalchemy.datamanager.NO_SAVEPOINT_SUPPORT = set([])



    def tearDownPloneSite(self, portal):
        session = create_session()
        for model in MODELS:
            getattr(model, 'metadata').drop_all(session.bind)
        getattr(task_model.Base, 'metadata').drop_all(session.bind)

OPENGEVER_INBOX_FIXTURE = InboxFunctionalLayer()
OPENGEVER_INBOX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_INBOX_FIXTURE,), name="OpengeverInbox:Integration")
