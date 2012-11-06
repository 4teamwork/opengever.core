from ftw.tabbedview.interfaces import ITabbedView
from opengever.globalindex import model
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.setuphandlers import create_sql_tables
from opengever.ogds.base.utils import create_session
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.testing import applyProfile
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


class TaskFunctionalLayer(PloneSandboxLayer):
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
        from opengever import document
        xmlconfig.file(
            'configure.zcml', package=document, context=configurationContext)
        from opengever import mail
        xmlconfig.file(
            'configure.zcml', package=mail, context=configurationContext)
        from ftw import tabbedview
        xmlconfig.file(
            'configure.zcml', package=tabbedview, context=configurationContext)
        from ftw import contentmenu
        xmlconfig.file(
            'configure.zcml',
            package=contentmenu,
            context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'opengever.task:default')
        applyProfile(portal, 'opengever.document:default')
        applyProfile(portal, 'opengever.mail:default')
        applyProfile(portal, 'opengever.ogds.base:default')
        applyProfile(portal, 'ftw.tabbedview:default')
        applyProfile(portal, 'ftw.contentmenu:default')

        create_sql_tables()
        session = create_session()

        model.Base.metadata.create_all(session.bind)

        # configure client ID
        registry = getUtility(IRegistry, context=portal)
        proxy = registry.forInterface(IClientConfiguration)
        proxy.client_id

        tab_reg = registry.forInterface(ITabbedView)
        tab_reg.batch_size = 5

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
            ('og_mandant1_users', 'og_mandant1_inbox', 'og_mandant2_users'))

        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory('Folder', 'Members')
        portal['Members'].invokeFactory('Folder', TEST_USER_ID)

        # savepoint "support" for sqlite
        # We need savepoint support for version retrieval with CMFEditions.
        import zope.sqlalchemy.datamanager
        zope.sqlalchemy.datamanager.NO_SAVEPOINT_SUPPORT = set([])


OPENGEVER_TASK_FIXTURE = TaskFunctionalLayer()
OPENGEVER_TASK_INTEGRATION_TESTING = FunctionalTesting(
    bases=(OPENGEVER_TASK_FIXTURE, ),
    name="OpengeverTask:Integration")
