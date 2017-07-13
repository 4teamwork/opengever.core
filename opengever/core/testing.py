from collective.taskqueue.interfaces import ITaskQueue
from collective.transmogrifier import transmogrifier
from ftw.builder import session
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import set_builder_session_factory
from ftw.bumblebee.tests.helpers import BumblebeeTestTaskQueue
from ftw.testbrowser import TRAVERSAL_BROWSER_FIXTURE
from ftw.testing import ComponentRegistryLayer
from ftw.testing import TransactionInterceptor
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from ftw.testing.quickinstaller import snapshots
from opengever.activity.interfaces import IActivitySettings
from opengever.base import pdfconverter
from opengever.base.model import create_session
from opengever.base.pdfconverter import pdfconverter_available_lock
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.core import sqlite_testing
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings # noqa
from opengever.meeting.interfaces import IMeetingSettings
from opengever.officeatwork.interfaces import IOfficeatworkSettings
from opengever.private import enable_opengever_private
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import logout
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.browserlayer.utils import unregister_layer
from plone.dexterity.schema import SCHEMA_CACHE
from plone.protect.auto import safeWrite
from plone.testing import z2
from plone.transformchain.interfaces import ITransform
from Products.CMFCore.utils import getToolByName
from Testing.ZopeTestCase.utils import setupCoreSessions
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.configuration import xmlconfig
from zope.globalrequest import setRequest
from zope.sqlalchemy.datamanager import mark_changed
from ZPublisher.interfaces import IPubAfterTraversal
import logging
import os
import sys
import transaction


loghandler = logging.StreamHandler(stream=sys.stdout)
loghandler.setLevel(logging.WARNING)
for name, level in {'plone.protect': logging.INFO,
                    'opengever.base.protect': logging.INFO}.items():
    logger = logging.getLogger(name)
    logger.addHandler(loghandler)
    logger.setLevel(level)


snapshots.disable()


def clear_transmogrifier_registry():
    transmogrifier.configuration_registry._config_info = {}
    transmogrifier.configuration_registry._config_ids = []


def toggle_feature(registry_interface, enabled=True):

    api.portal.set_registry_record('is_feature_enabled', enabled,
                                   interface=registry_interface)
    transaction.commit()


def activate_meeting():
    toggle_feature(IMeetingSettings, enabled=True)


def activate_meeting_word_implementation():
    api.portal.set_registry_record('is_word_implementation_enabled', True,
                                   interface=IMeetingSettings)
    # The meeting feature must be activated too for having an effect.
    activate_meeting()


def deactivate_activity_center():
    toggle_feature(IActivitySettings, enabled=False)


def activate_activity_center():
    toggle_feature(IActivitySettings, enabled=True)


def activate_officeatwork():
    toggle_feature(IOfficeatworkSettings, enabled=True)


def deactivate_bumblebee_feature():
    toggle_feature(IGeverBumblebeeSettings, enabled=False)


def activate_bumblebee_feature():
    toggle_feature(IGeverBumblebeeSettings, enabled=True)


class PDFConverterAvailability(object):
    """Context manager that allows for safeley monkey patching
    PDFCONVERTER_AVAILABLE during tests, reverting the flag to whatever
    original value it had.
    """

    def __init__(self, value):
        self.value = value
        self.original_value = pdfconverter.PDFCONVERTER_AVAILABLE

    def __enter__(self):
        lock_acquired = pdfconverter_available_lock.acquire(False)
        if not lock_acquired:
            raise Exception(
                "Failed to acquire lock for mutating PDFCONVERTER_AVAILABLE."
                "This means you're probably running tests in several threads ",
                "which wasn't originall intended. Acquiring this lock in "
                "blocking mode could lead to lock contention and serious, "
                "hard to spot performance degradation, which is why we "
                "won't allow you to do this without looking at it again.")

        pdfconverter.PDFCONVERTER_AVAILABLE = self.value

    def __exit__(self, exc_type, exc_val, exc_tb):
        pdfconverter.PDFCONVERTER_AVAILABLE = self.original_value
        pdfconverter_available_lock.release()


class AnnotationLayer(ComponentRegistryLayer):
    """Loads ZML of zope.annotation.
    """

    def setUp(self):
        super(AnnotationLayer, self).setUp()
        import zope.annotation
        self.load_zcml_file('configure.zcml', zope.annotation)


ANNOTATION_LAYER = AnnotationLayer()


class OpengeverFixture(PloneSandboxLayer):
    defaultBases = (COMPONENT_REGISTRY_ISOLATION, BUILDER_LAYER)

    def __init__(self, bases=None, name=None,
                 sql_layer=sqlite_testing.SQLITE_MEMORY_FIXTURE):
        bases = (bases or self.defaultBases) + (sql_layer, )
        name = name or ':'.join((self.__class__.__name__,
                                 sql_layer.__class__.__name__))
        super(OpengeverFixture, self).__init__(bases=bases, name=name)

    def setUpZope(self, app, configurationContext):
        # do not install pas plugins (doesnt work in tests)
        from opengever.ogds.base import hooks
        hooks._setup_scriptable_plugin = lambda *a, **kw: None

        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'

            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'

            '  <include package="opengever.ogds.base" file="tests.zcml" />'
            '  <include package="opengever.base.tests" file="tests.zcml" />'
            '  <include package="opengever.testing" file="tests.zcml" />'
            '  <include package="opengever.setup.tests" />'

            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'plone.app.versioningbehavior')
        z2.installProduct(app, 'collective.taskqueue.pasplugin')

        setupCoreSessions(app)

        # Set max subobject limit to 0 -> unlimited
        # In tests this is set to 100 by default
        transient_object_container = app.temp_folder.session_data
        transient_object_container.setSubobjectLimit(0)

        os.environ['BUMBLEBEE_DEACTIVATE'] = "True"

        import opengever.base.tests.views
        xmlconfig.file('configure.zcml',
                       opengever.base.tests.views,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        self.installOpengeverProfiles(portal)
        self.setupLanguageTool(portal)
        self.allowAllTypes(portal)
        deactivate_activity_center()
        deactivate_bumblebee_feature()

    def tearDown(self):
        super(OpengeverFixture, self).tearDown()
        clear_transmogrifier_registry()

    def tearDownZope(self, app):
        super(OpengeverFixture, self).tearDownZope(app)
        os.environ['BUMBLEBEE_DEACTIVATE'] = "True"

    def installOpengeverProfiles(self, portal):
        applyProfile(portal, 'opengever.core:default')
        applyProfile(portal, 'opengever.testing:testing')

    def createMemberFolder(self, portal):
        # Create a Members folder.
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory('Folder', 'Members')
        portal['Members'].invokeFactory('Folder', TEST_USER_ID)
        setRoles(portal, TEST_USER_ID, ['Member'])

    def setupLanguageTool(self, portal):
        """Configure the language tool as close as possible to production,
        without breaking most of the existing tests.
        """
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('en')
        lang_tool.supported_langs = ['en']

    def allowAllTypes(self, portal):
        """Some tests rely on being able to add things to the site root.
        Because of historical reasons we therefore set filter_content_types
        to False in order to allow that.
        We need to change the tests in the future so that we no longer need
        to do that.
        """
        portal.portal_types['Plone Site'].filter_content_types = False


def functional_session_factory():
    sess = session.BuilderSession()
    sess.auto_commit = True
    sess.session = create_session()
    return sess


def memory_session_factory():
    sqlite_testing.setup_memory_database()
    sess = session.BuilderSession()
    sess.auto_commit = False
    sess.auto_flush = True
    sess.session = create_session()
    return sess


MEMORY_DB_LAYER = sqlite_testing.StandaloneMemoryDBLayer(
    bases=(BUILDER_LAYER,
           set_builder_session_factory(memory_session_factory)),
    name='opengever:core:memory_db')

OPENGEVER_FIXTURE_SQLITE = OpengeverFixture(
    sql_layer=sqlite_testing.SQLITE_MEMORY_FIXTURE)

# OPENGEVER_FIXTURE is the default fixture used in policy tests.
OPENGEVER_FIXTURE = OPENGEVER_FIXTURE_SQLITE

OPENGEVER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_FIXTURE_SQLITE,
           set_builder_session_factory(functional_session_factory)),
    name="opengever.core:functional")

OPENGEVER_FUNCTIONAL_ZSERVER_TESTING = FunctionalTesting(
    bases=(z2.ZSERVER_FIXTURE,
           OPENGEVER_FIXTURE_SQLITE,
           set_builder_session_factory(functional_session_factory)),
    name="opengever.core:functional:zserver")


def activate_filing_number(portal):
    applyProfile(portal, 'opengever.dossier:filing')
    transaction.commit()


def inactivate_filing_number(portal):
    unregister_layer('opengever.dossier.filing')

    portal_types = getToolByName(portal, 'portal_types')
    fti = portal_types.get('opengever.dossier.businesscasedossier')
    fti.behaviors = [behavior for behavior in fti.behaviors
                     if not behavior.endswith('IFilingNumber')]

    SCHEMA_CACHE.invalidate('opengever.dossier.businesscasedossier')


class FilingLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING,)

    def setUpPloneSite(self, portal):
        activate_filing_number(portal)


OPENGEVER_FUNCTIONAL_FILING_LAYER = FilingLayer()


class MeetingLayer(PloneSandboxLayer):

    def setUpPloneSite(self, portal):
        activate_meeting()

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING,)


OPENGEVER_FUNCTIONAL_MEETING_LAYER = MeetingLayer()


class ActivityLayer(PloneSandboxLayer):

    def setUpPloneSite(self, portal):
        activate_activity_center()

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING,)


OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER = ActivityLayer()


class DossierTemplateLayer(PloneSandboxLayer):

    def setUpPloneSite(self, portal):
        toggle_feature(IDossierTemplateSettings, enabled=True)

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING,)


OPENGEVER_FUNCTIONAL_DOSSIER_TEMPLATE_LAYER = DossierTemplateLayer()


class BumblebeeLayer(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        super(BumblebeeLayer, self).setUpZope(app, configurationContext)

        self.queue = BumblebeeTestTaskQueue()
        sm = getSiteManager()
        sm.registerUtility(self.queue, provided=ITaskQueue, name='test-queue')

    def setUpPloneSite(self, portal):
        activate_bumblebee_feature()

    def testSetUp(self):
        super(BumblebeeLayer, self).testSetUp()
        self.reset_environment_variables()

    def tearDownZope(self, app):
        super(BumblebeeLayer, self).tearDownZope(app)
        self.reset_environment_variables()

    def reset_environment_variables(self):
        os.environ['BUMBLEBEE_APP_ID'] = 'local'
        os.environ['BUMBLEBEE_SECRET'] = 'secret'
        os.environ['BUMBLEBEE_INTERNAL_PLONE_URL'] = 'http://nohost/plone'
        os.environ['BUMBLEBEE_PUBLIC_URL'] = 'http://bumblebee'
        os.environ.pop('BUMBLEBEE_INTERNAL_URL', None)
        os.environ.pop('BUMBLEBEE_DEACTIVATE', None)

    def testTearDown(self):
        self.queue.reset()
        super(BumblebeeLayer, self).testTearDown()

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING,)


OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER = BumblebeeLayer()


class PrivateFolderLayer(PloneSandboxLayer):

    def setUpPloneSite(self, portal):
        enable_opengever_private()

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING,)


OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER = PrivateFolderLayer()


class OfficeatworkLayer(PloneSandboxLayer):

    def setUpPloneSite(self, portal):
        activate_officeatwork()

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING,)


OPENGEVER_FUNCTIONAL_OFFICEATWORK_LAYER = OfficeatworkLayer()


class ContentFixtureLayer(OpengeverFixture):
    """The content fixture layer extends the regular OpengeverFixture with a
    content fixture.
    The content fixture is a set of objects which are constructed on layer setup
    time and can be used by all tests, saving us the per-test creation time.

    SQL:
    This fixture does only work with sqlite at the moment. It cannot base on the
    SQLITE_MEMORY_FIXTURE because this will break savepoint support because the
    engine would be created before the ZCML is loaded, registering engine
    creation event handlers.

    Builder session:
    ftw.builder provides testing layers and functions for using builders within
    tests.
    It does not provide infrastructure for setting up builders in layer setup.
    Therefore we cannot reuse ftw.builder's testing layers but configure the
    builder manually in a non-committing integration testing mode.

    Warning:
    Do not create another fixture layer based on this fixture layer.
    It won't work without fixing transactionality issues.
    The current setup works because the fixture state is committed to the database.
    Committed state cannot be rolled back.
    Uncommitted state will get lost when IntegrationTesting.testSetUp begins
    a new transaction.
    """


    defaultBases = (COMPONENT_REGISTRY_ISOLATION, )

    def __init__(self):
        # By super-super-calling the __init__ we remove the SQL bases,
        # since we are implementing SQL setup in this layer directly.
        PloneSandboxLayer.__init__(self)

    def setUpZope(self, app, configurationContext):
        super(ContentFixtureLayer, self).setUpZope(app, configurationContext)
        # Setting up the database, which creates a new engine, must happen after
        # opengever's ZCML is loaded in order to have engine creation event
        # handlers already registered, which enable support for rolling back
        # to savepoints.
        sqlite_testing.setup_memory_database()
        sqlite_testing.create_tables()

    def setUpPloneSite(self, portal):
        session.current_session = session.BuilderSession()
        session.current_session.session = create_session()
        super(ContentFixtureLayer, self).setUpPloneSite(portal)

        portal.portal_languages.use_combined_language_codes = True
        portal.portal_languages.addSupportedLanguage('de-ch')

        # Avoid circular imports:
        from opengever.testing.fixtures import OpengeverContentFixture
        setRequest(portal.REQUEST)
        self['fixture_lookup_table'] = OpengeverContentFixture()()
        setRequest(None)

    def tearDown(self):
        sqlite_testing.model.Session.close_all()
        sqlite_testing.truncate_tables()
        super(ContentFixtureLayer, self).tearDown()
        session.current_session = None

    def allowAllTypes(self, portal):
        """In the fixture layer, the fixture objects should be used and
        we want them to be at the correct place hierarchically.
        When additional objects need to be created anyway, they can be placed
        in the correct spot easily by using the fixture objects as parents.
        Therefore we do not allow to create objects at the portal.
        """
        pass


class GEVERIntegrationTesting(IntegrationTesting):
    """Custom integration testing extension:
    1. Make savepoint at test begin and rollback after the test.
    2. Prevent all interaction with transactions, primarily in order to avoid
       having data committed which can then not be rolled back anymore.
    """

    def setUp(self):
        super(GEVERIntegrationTesting, self).setUp()
        transaction.commit()
        self.interceptor = TransactionInterceptor().install()
        getGlobalSiteManager().registerHandler(
            self.handlePubAfterTraversal, [IPubAfterTraversal])

    def tearDown(self):
        self.interceptor.uninstall()
        super(GEVERIntegrationTesting, self).tearDown()

    def testSetUp(self):
        super(GEVERIntegrationTesting, self).testSetUp()
        # In order to let the SQL transaction manager make a savepoint of no
        # changes we need to mark the session as changed first.
        mark_changed(create_session())
        self.savepoint = transaction.savepoint()
        self.interceptor.intercept(self.interceptor.BEGIN
                                   | self.interceptor.COMMIT
                                   | self.interceptor.ABORT)
        self.interceptor.begin_savepoint_simulation()
        self.interceptor.begin()
        logout()

    def testTearDown(self):
        self.interceptor.stop_savepoint_simulation()
        self.savepoint.rollback()
        self.savepoint = None
        self.interceptor.clear().intercept(self.interceptor.COMMIT)
        super(GEVERIntegrationTesting, self).testTearDown()

    def handlePubAfterTraversal(self, event):
        """Support plone.protect's auto CSRF protection as good as possible.

        The problem is that we use the same connection and transaction for
        preparation as for performing a request with ftw.testbrowser.

        This means that we may already have changed objects on the connection
        but the change is not from within the request.

        We fix that by marking all objects which are already marked as changed
        on the current as safe for CSRF.
        This also means that the auto protection does no longer trigger within
        the test for the followed requests.
        """
        transform = getMultiAdapter((self['portal'], event.request),
                                    ITransform,
                                    name='plone.protect.autocsrf')
        for obj in transform._registered_objects():
            safeWrite(obj, event.request)


OPENGEVER_INTEGRATION_TESTING = GEVERIntegrationTesting(
    # Warning: do not try to base other layers on ContentFixtureLayer.
    # See docstring of ContentFixtureLayer.
    bases=(ContentFixtureLayer(), TRAVERSAL_BROWSER_FIXTURE),
    name="opengever.core:integration")
