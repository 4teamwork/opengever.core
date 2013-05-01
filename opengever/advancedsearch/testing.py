from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.setuphandlers import create_sql_tables
from opengever.ogds.base.utils import create_session
from plone.app.testing import applyProfile, IntegrationTesting, \
    PloneSandboxLayer, PLONE_FIXTURE, setRoles, \
    TEST_USER_ID, FunctionalTesting
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.configuration import xmlconfig
from opengever.ogds.base.setuphandlers import _create_example_client, _create_example_user
from opengever.globalindex import model


class BaseLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # do not install pas plugins (doesnt work in tests)
        from opengever.ogds.base import setuphandlers
        setuphandlers.setup_scriptable_plugin = lambda *a, **kw: None
        # Load configure.zcml

        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'

            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'

            '  <include package="opengever.ogds.base" file="tests.zcml" />'

            '</configure>',
            context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'opengever.base:default')
        applyProfile(portal, 'opengever.task:default')
        applyProfile(portal, 'opengever.ogds.base:default')
        applyProfile(portal, 'opengever.dossier:default')
        applyProfile(portal, 'opengever.document:default')

        # setup the sql tables
        create_sql_tables()
        session = create_session()

        model.Base.metadata.create_all(session.bind)

        _create_example_client(session, 'plone',
                              {'title': 'Plone',
                              'ip_address': '127.0.0.1',
                              'site_url': 'http://nohost/plone',
                              'public_url': 'http://nohost/plone',
                              'group': 'og_mandant1_users',
                              'inbox_group': 'og_mandant1_inbox'})


        _create_example_user(session, portal, TEST_USER_ID,{
          'firstname': 'Test',
          'lastname': 'User',
          'email': 'test.user@local.ch',
          'email2': 'test_user@private.ch'},
          ('og_mandant1_users','og_mandant1_inbox', 'og_mandant2_users'))


        # configure client ID
        registry = getUtility(IRegistry, context=portal)
        client = registry.forInterface(IClientConfiguration)
        client.client_id = u'plone'

        # browser tester roles
        setRoles(portal, TEST_USER_ID, ['Member', 'Contributor', 'Manager'])

OPENGEVER_ADV_SEARCH_FIXTURE = BaseLayer()
OPENGEVER_ADV_SEARCH_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_ADV_SEARCH_FIXTURE,), name="OpengeverAdvancedsearch:Integration")
OPENGEVER_ADV_SEARCH_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_ADV_SEARCH_FIXTURE,), name="OpengeverAdvancedsearch:Functional")
