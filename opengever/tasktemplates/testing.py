from opengever.ogds.base.setuphandlers import create_sql_tables
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from plone.app.testing import TEST_USER_ID, SITE_OWNER_NAME, setRoles
from opengever.ogds.base.utils import create_session
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from zope.configuration import xmlconfig
from opengever.globalindex import model


class TaskTemplatesFunctionalLayer(PloneSandboxLayer):
    """Layer for integration tests."""

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # do not install pas plugins (doesnt work in tests)

        from opengever.ogds import base
        from opengever.ogds.base import setuphandlers

        setuphandlers.setup_scriptable_plugin = lambda *a, **kw: None

        xmlconfig.file(
            'tests.zcml', package=base, context=configurationContext)
        from opengever import task
        xmlconfig.file(
            'configure.zcml', package=task, context=configurationContext)
        from opengever import tasktemplates
        xmlconfig.file(
            'configure.zcml',
            package=tasktemplates, context=configurationContext)
        from opengever import dossier
        xmlconfig.file(
            'configure.zcml',
            package=dossier, context=configurationContext)
        from opengever import tabbedview
        xmlconfig.file(
            'configure.zcml',
            package=tabbedview, context=configurationContext)
        from opengever import contact
        xmlconfig.file(
            'configure.zcml',
            package=contact, context=configurationContext)
        from ftw import table
        xmlconfig.file(
            'configure.zcml',
            package=table, context=configurationContext)
        from ftw import contentmenu
        xmlconfig.file(
            'configure.zcml',
            package=contentmenu, context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'opengever.task:default')
        applyProfile(portal, 'opengever.tasktemplates:default')
        applyProfile(portal, 'opengever.dossier:default')
        applyProfile(portal, 'opengever.ogds.base:default')
        applyProfile(portal, 'opengever.tabbedview:default')
        applyProfile(portal, 'opengever.contact:default')
        applyProfile(portal, 'ftw.contentmenu:default')
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
        portal.invokeFactory('Folder', 'Members')
        portal['Members'].invokeFactory('Folder', TEST_USER_ID)


OPENGEVER_TASKTEMPLATES_FIXTURE = TaskTemplatesFunctionalLayer()
OPENGEVER_TASKTEMPLATES_INTEGRATION_TESTING = FunctionalTesting(
    bases=(OPENGEVER_TASKTEMPLATES_FIXTURE, ),
    name="OpengeverTaskTemplates:Integration")
