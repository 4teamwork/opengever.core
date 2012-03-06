from opengever.globalindex import model as task_model
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import create_sql_tables, MODELS
from opengever.ogds.base.utils import create_session
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.directives import form
from plone.registry.interfaces import IRegistry
from plone.testing import Layer
from plone.testing import zca
from zope.component import getUtility
from zope.configuration import xmlconfig


class AnnotationLayer(Layer):
    """Loads ZML of zope.annotation.
    """

    defaultBases = (zca.ZCML_DIRECTIVES,)

    def testSetUp(self):
        self['configurationContext'] = zca.stackConfigurationContext(
            self.get('configurationContext'))

        import zope.annotation
        xmlconfig.file('configure.zcml', zope.annotation,
                       context=self['configurationContext'])

    def testTearDown(self):
        del self['configurationContext']


ANNOTATION_LAYER = AnnotationLayer()


class BaseFunctionalLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # do not install pas plugins (doesnt work in tests)
         from opengever.ogds.base import setuphandlers
         setuphandlers.setup_scriptable_plugin = lambda *a, **kw: None

         from plone.app import dexterity
         self.loadZCML('meta.zcml', package=dexterity)
         self.loadZCML('configure.zcml', package=dexterity)

         from opengever.ogds import base
         self.loadZCML('tests.zcml', package=base)
         self.loadZCML('configure.zcml', package=base)

         from opengever import repository
         self.loadZCML('configure.zcml', package=repository)

         from opengever import document
         self.loadZCML('configure.zcml', package=document)

         from opengever.base import tests
         xmlconfig.file('testing.zcml', package=tests,
             context=configurationContext)


    def setUpPloneSite(self, portal):

        # Install the example.conference product
        applyProfile(portal, 'plone.app.dexterity:default')
        applyProfile(portal, 'opengever.base:default')
        applyProfile(portal, 'opengever.repository:default')
        applyProfile(portal, 'opengever.document:default')

        # setup the sql tables
        create_sql_tables()
        session = create_session()
        task_model.Base.metadata.create_all(session.bind)

        _create_example_client(session, 'plone',
                              {'title': 'Plone',
                              'ip_address': '127.0.0.1',
                              'site_url': 'http://nohost/plone',
                              'public_url': 'http://nohost/plone',
                              'group': 'og_mandant1_users',
                              'inbox_group': 'og_mandant1_inbox'})

        # configure client ID
        registry = getUtility(IRegistry, context=portal)
        client = registry.forInterface(IClientConfiguration)
        client.client_id = u'plone'

        from plone.app.testing import setRoles, TEST_USER_ID
        setRoles(portal, TEST_USER_ID, ['Member', 'Contributor', 'Editor'])

        # Disable the prevent_deletion subscriber. In tests, we WANT
        # to be able to quickly delete objs without becoming Manager
        from opengever.base import subscribers
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.unregisterHandler(subscribers.prevent_deletion)

    def tearDownPloneSite(self, portal):
        session = create_session()
        for model in MODELS:
            getattr(model, 'metadata').drop_all(session.bind)
        getattr(task_model.Base, 'metadata').drop_all(session.bind)

OPENGEVER_BASE_FIXTURE = BaseFunctionalLayer()
OPENGEVER_BASE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_BASE_FIXTURE,), name="OpengeverBase:Integration")


class IEmptySchema(form.Schema):
    """an empty schema used or tests"""
