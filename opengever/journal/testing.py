from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.utils import create_session
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles, TEST_USER_ID


class JournalLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE, )

    def setUpPloneSite(self, portal):
        session = create_session()
        _create_example_client(session, 'plone',
                              {'title': 'plone',
                              'ip_address': '127.0.0.1',
                              'site_url': 'http://nohost/plone',
                              'public_url': 'http://nohost/plone',
                              'group': 'og_mandant1_users',
                              'inbox_group': 'og_mandant1_inbox'})

        _create_example_user(session, portal, TEST_USER_ID, {
            'firstname': 'Test',
            'lastname': 'User',
            'email': 'test.user@local.ch',
            'email2': 'test_user@private.ch'},
            ('og_mandant1_users', 'og_mandant1_inbox', ))

        setRoles(portal, TEST_USER_ID, ['Member', 'Manager', 'Editor'])

    def tearDown(self):
        super(JournalLayer, self).tearDown()
        truncate_sql_tables()


OPENGEVER_JOURNAL_FIXTURE = JournalLayer()
OPENGEVER_JOURNAL_INTEGRATION_TESTING = FunctionalTesting(
    bases=(OPENGEVER_JOURNAL_FIXTURE, ),
    name="OpengeverJournal:Integration")
