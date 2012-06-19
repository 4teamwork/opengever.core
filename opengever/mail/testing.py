from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile
from opengever.ogds.base.setuphandlers import MODELS
from opengever.globalindex import model as task_model
from opengever.ogds.base.utils import create_session
from plone.app.testing import IntegrationTesting
from zope.configuration import xmlconfig
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from plone.app.testing import setRoles, TEST_USER_ID, login
from opengever.ogds.base.setuphandlers import create_sql_tables


class MailIntegrationLayer(PloneSandboxLayer):
    """Layer for integration tests."""

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # do not install pas plugins (doesnt work in tests)
        from opengever.ogds.base import setuphandlers
        setuphandlers.setup_scriptable_plugin = lambda *a, **kw: None

        from opengever.mail import tests
        xmlconfig.file('testing.zcml', package=tests,
                       context=configurationContext)

        from ftw import mail
        xmlconfig.file('configure.zcml', package=mail,
                       context=configurationContext)

    def setUpPloneSite(self, portal):

        applyProfile(portal, 'opengever.ogds.base:default')
        applyProfile(portal, 'opengever.mail:default')
        applyProfile(portal, 'ftw.mail:default')
        applyProfile(portal, 'opengever.base:default')
        applyProfile(portal, 'opengever.document:default')
        applyProfile(portal, 'opengever.dossier:default')
        applyProfile(portal, 'ftw.tabbedview:default')

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
            'mail-test',
            {'firstname': 'Test',
             'lastname': 'User',
             'email': 'test.user@local.ch',
             'email2': 'test_user@private.ch'},
            ('client1_users',
            'client1_inbox_users'))

        # configure client ID
        registry = getUtility(IRegistry)
        registry['opengever.ogds.base.interfaces.'
                 'IClientConfiguration.client_id'] = u'client1'
        registry['opengever.base.interfaces.IBaseClientID.client_id'] = u'OG'

        setRoles(portal, TEST_USER_ID, ['Member', 'Contributor', 'Editor'])
        login(portal, 'mail-test')

    def tearDownPloneSite(self, portal):
        session = create_session()
        for model in MODELS:
            getattr(model, 'metadata').drop_all(session.bind)
        getattr(task_model.Base, 'metadata').drop_all(session.bind)

OPENGEVER_MAIL_FIXTURE = MailIntegrationLayer()
OPENGEVER_MAIL_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_MAIL_FIXTURE,), name="OpengeverMail:Integration")


class MockEvent(object):

    #History: [[interface, context], ]
    event_history = []

    def mock_handler(self, event):
        self.event_history.append(event, )

    def last_event(self):
        return self.event_history[-1]
