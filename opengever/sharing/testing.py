from opengever.globalindex import model
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.setuphandlers import create_sql_tables
from opengever.ogds.base.utils import create_session
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import setRoles, TEST_USER_ID
from zope.configuration import xmlconfig


class OpengeverSharingIntegrationLayer(PloneSandboxLayer):
    """Layer for integration tests."""

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # do not install pas plugins (doesnt work in tests)
        from opengever.ogds import base
        from opengever.ogds.base import setuphandlers
        setuphandlers.setup_scriptable_plugin = lambda *a, **kw: None
        xmlconfig.file(
            'tests.zcml', package=base, context=configurationContext)

        from opengever import dossier
        xmlconfig.file(
            'configure.zcml',
            package=dossier, context=configurationContext)
        from opengever import tabbedview
        xmlconfig.file(
            'configure.zcml',
            package=tabbedview, context=configurationContext)
        from opengever import journal
        xmlconfig.file(
            'configure.zcml',
            package=journal, context=configurationContext)
        from opengever import repository
        xmlconfig.file(
            'configure.zcml',
            package=repository, context=configurationContext)
        from ftw import table
        xmlconfig.file(
            'configure.zcml',
            package=table, context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'opengever.ogds.base:default')
        applyProfile(portal, 'opengever.dossier:default')
        applyProfile(portal, 'opengever.tabbedview:default')
        applyProfile(portal, 'opengever.journal:default')
        applyProfile(portal, 'opengever.repository:default')
        applyProfile(portal, 'ftw.table:default')
        applyProfile(portal, 'opengever.sharing:default')

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

        setRoles(
            portal,
            TEST_USER_ID, ['Manager', 'Contributor', 'Editor'])

OPENGEVER_SHARING_FIXTURE = OpengeverSharingIntegrationLayer()
OPENGEVER_SHARING_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_SHARING_FIXTURE, ),
    name="OpengeverSharing:Integration")
