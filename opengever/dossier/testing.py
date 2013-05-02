from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.utils import create_session
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class DossierLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE, )

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
            SITE_OWNER_NAME,
            {'firstname': 'Test',
             'lastname': 'User',
             'email': 'test.user@local.ch',
             'email2': 'test_user@private.ch'},
            ('client1_users',
            'client1_inbox_users'))

        # configure client ID
        registry = getUtility(IRegistry, context=portal)
        client = registry.forInterface(IClientConfiguration)
        client.client_id = u'client1'

        from plone.app.testing import setRoles, TEST_USER_ID
        setRoles(portal, TEST_USER_ID, ['Member', 'Contributor', 'Editor'])

    def tearDown(self):
        super(DossierLayer, self).tearDown()
        truncate_sql_tables()

OPENGEVER_DOSSIER_FIXTURE = DossierLayer()
OPENGEVER_DOSSIER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_DOSSIER_FIXTURE, ), name="OpengeverDossier:Integration")
OPENGEVER_DOSSIER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_DOSSIER_FIXTURE, ), name="OpengeverDossier:Functional")
