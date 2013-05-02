from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.utils import create_session
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles


class TaskTemplatesLayer(PloneSandboxLayer):
    defaultBases = (OPENGEVER_FIXTURE, )

    def setUpPloneSite(self, portal):
        session = create_session()

        # configure client ID
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

        _create_example_user(session, portal, TEST_USER_ID, {
            'firstname': 'Test',
            'lastname': 'User',
            'email': 'test.user@local.ch',
            'email2': 'test_user@private.ch'},
            ('og_mandant1_users', 'og_mandant1_inbox', 'og_mandant2_users', ))

        _create_example_user(session, portal, SITE_OWNER_NAME, {
            'firstname': 'Site',
            'lastname': 'Owner',
            'email': 'site.owner@local.ch',
            'email2': 'site_owner@private.ch'},
            ('og_mandant2_users', ))

        setRoles(portal, TEST_USER_ID, ['Manager'])

    def tearDown(self):
        super(TaskTemplatesLayer, self).tearDown()
        truncate_sql_tables()


OPENGEVER_TASKTEMPLATES_FIXTURE = TaskTemplatesLayer()
OPENGEVER_TASKTEMPLATES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_TASKTEMPLATES_FIXTURE, ),
    name="OpengeverTaskTemplates:Functional")
