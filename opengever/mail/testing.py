from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.utils import create_session
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles, TEST_USER_ID, login
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class MailIntegrationLayer(PloneSandboxLayer):
    """Layer for integration tests."""

    defaultBases = (OPENGEVER_FIXTURE,)

    def setUpPloneSite(self, portal):
        session = create_session()
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

    def tearDown(self):
        super(MailIntegrationLayer, self).tearDown()
        truncate_sql_tables()


OPENGEVER_MAIL_FIXTURE = MailIntegrationLayer()
OPENGEVER_MAIL_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_MAIL_FIXTURE,), name="OpengeverMail:Integration")

OPENGEVER_MAIL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_MAIL_FIXTURE,), name="OpengeverMail:Functional")


class MockEvent(object):

    #History: [[interface, context], ]
    event_history = []

    def mock_handler(self, event):
        self.event_history.append(event, )

    def last_event(self):
        return self.event_history[-1]
