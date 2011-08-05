from opengever.ogds.base.setuphandlers import create_sql_tables
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.utils import create_session
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.configuration import xmlconfig


class DocumentFunctionalLayer(PloneSandboxLayer):
    """Layer for integration tests."""

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # do not install pas plugins (doesnt work in tests)
        from opengever.ogds.base import setuphandlers
        setuphandlers.setup_scriptable_plugin = lambda *a, **kw: None

        from opengever import document
        xmlconfig.file('configure.zcml', package=document,
            context=configurationContext)
        xmlconfig.file('tests.zcml', package=document,
            context=configurationContext)

        from opengever import base
        xmlconfig.file('configure.zcml', package=base,
            context=configurationContext)


    def setUpPloneSite(self, portal):
        applyProfile(portal, 'opengever.document:default')
        applyProfile(portal, 'opengever.ogds.base:default')
        applyProfile(portal, 'opengever.base:default')
        applyProfile(portal, 'ftw.tabbedview:default')

        # create test ogds
        create_sql_tables()
        session = create_session()

        _create_example_client(session, 'plone',
                              {'title': 'Plone',
                              'ip_address': '127.0.0.1',
                              'site_url': 'http://nohost/plone',
                              'public_url': 'http://nohost/plone',
                              'group': 'og_mandant1_users',
                              'inbox_group': 'og_mandant1_inbox'})

        # fix registry
        registry = getUtility(IRegistry)
        registry['opengever.ogds.base.interfaces.'
                 'IClientConfiguration.client_id'] = u'plone'
        registry['ftw.tabbedview.interfaces.ITabbedView.batch_size'] = 50

        from plone.app.testing import setRoles, TEST_USER_ID
        setRoles(portal, TEST_USER_ID, ['Member', 'Contributor', 'Editor'])


OPENGEVER_DOCUMENT_FIXTURE = DocumentFunctionalLayer()
OPENGEVER_DOCUMENT_INTEGRATION_TESTING = FunctionalTesting(
    bases=(OPENGEVER_DOCUMENT_FIXTURE, ),
    name="OpengeverDocument:Integration")
