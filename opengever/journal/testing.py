from opengever.core.testing import truncate_sql_tables
from opengever.globalindex import model
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.setuphandlers import create_sql_tables
from opengever.ogds.base.utils import create_session
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import setRoles, TEST_USER_ID
from zope.configuration import xmlconfig


class OpengeverJournalFunctionalLayer(PloneSandboxLayer):
    """Layer for integration tests."""

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # do not install pas plugins (doesnt work in tests)
        from opengever.ogds.base import setuphandlers
        setuphandlers.setup_scriptable_plugin = lambda *a, **kw: None


        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'

            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'

            '  <include package="opengever.ogds.base" file="tests.zcml" />'

            '</configure>',
            context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'opengever.ogds.base:default')
        applyProfile(portal, 'opengever.tabbedview:default')
        applyProfile(portal, 'opengever.contact:default')
        applyProfile(portal, 'opengever.document:default')
        applyProfile(portal, 'opengever.dossier:default')
        applyProfile(portal, 'opengever.task:default')
        applyProfile(portal, 'opengever.trash:default')
        applyProfile(portal, 'opengever.mail:default')
        applyProfile(portal, 'opengever.repository:default')
        applyProfile(portal, 'ftw.table:default')

        create_sql_tables()
        session = create_session()

        model.Base.metadata.create_all(session.bind)

        # configure client ID
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
        super(OpengeverJournalFunctionalLayer, self).tearDown()
        truncate_sql_tables()

OPENGEVER_JOURNAL_FIXTURE = OpengeverJournalFunctionalLayer()
OPENGEVER_JOURNAL_INTEGRATION_TESTING = FunctionalTesting(
    bases=(OPENGEVER_JOURNAL_FIXTURE, ),
    name="OpengeverJournal:Integration")
