from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.utils import create_session
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.interfaces import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class InboxLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE,)

    def setUpPloneSite(self, portal):
        session = create_session()
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
            ('og_mandant1_users', 'og_mandant1_inbox'))

        # configure client ID
        registry = getUtility(IRegistry, context=portal)
        client = registry.forInterface(IClientConfiguration)
        client.client_id = u'plone'
        #
        # setRoles(portal, TEST_USER_ID, ['Member', 'Contributor', 'Editor'])

    def tearDown(self):
        super(InboxLayer, self).tearDown()
        truncate_sql_tables()

OPENGEVER_INBOX_FIXTURE = InboxLayer()
OPENGEVER_INBOX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_INBOX_FIXTURE,), name="OpengeverInbox:Integration")
OPENGEVER_INBOX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_INBOX_FIXTURE,), name="OpengeverInbox:Functional")
