from App.config import getConfiguration
from collective.taskqueue.interfaces import ITaskQueue
from collective.transmogrifier import transmogrifier
from ftw.builder import session
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import set_builder_session_factory
from ftw.bumblebee.tests.helpers import BumblebeeTestTaskQueue
from ftw.contentstats.logger import setup_logger
from ftw.testbrowser import TRAVERSAL_BROWSER_FIXTURE
from ftw.testing import ComponentRegistryLayer
from ftw.testing import FTWIntegrationTesting
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from ftw.testing.quickinstaller import snapshots
from opengever.activity.interfaces import IActivitySettings
from opengever.base.model import create_session
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.core import sqlite_testing
from opengever.core.cached_testing import CACHE_GEVER_FIXTURE
from opengever.core.cached_testing import CACHE_GEVER_INSTALLATION
from opengever.core.cached_testing import CACHED_COMPONENT_REGISTRY_ISOLATION
from opengever.core.cached_testing import DB_CACHE_MANAGER
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings  # noqa
from opengever.meeting.interfaces import IMeetingSettings
from opengever.officeatwork.interfaces import IOfficeatworkSettings
from opengever.private import enable_opengever_private
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import logout
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.browserlayer.utils import unregister_layer
from plone.dexterity.schema import SCHEMA_CACHE
from plone.testing import z2
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from Testing.ZopeTestCase.utils import setupCoreSessions
from unittest import TestCase
from zope.component import getSiteManager
from zope.configuration import xmlconfig
from zope.globalrequest import setRequest
from zope.sqlalchemy import datamanager
from zope.sqlalchemy.datamanager import mark_changed
import logging
import os
import shutil
import sys
import tempfile
import transaction
import ZConfig


loghandler = logging.StreamHandler(stream=sys.stdout)
loghandler.setLevel(logging.WARNING)
for name, level in {'plone.protect': logging.INFO,
                    'plone.app.viewletmanager': logging.ERROR,
                    'opengever.base.protect': logging.INFO}.items():
    logger = logging.getLogger(name)
    logger.addHandler(loghandler)
    logger.setLevel(level)


snapshots.disable()
TestCase.longMessage = True


def clear_transmogrifier_registry():
    transmogrifier.configuration_registry._config_info = {}
    transmogrifier.configuration_registry._config_ids = []


def toggle_feature(registry_interface, enabled=True):

    api.portal.set_registry_record('is_feature_enabled', enabled,
                                   interface=registry_interface)
    transaction.commit()


def activate_meeting():
    toggle_feature(IMeetingSettings, enabled=True)


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


class ComponentUnitTesting(ComponentRegistryLayer):
    """Testing layer for unit-testing zope components.
    This test provides isolation of the component registry and the site hooks
    as well as minimal components such as annotations.
    """

    def setUp(self):
        super(ComponentUnitTesting, self).setUp()
        import zope.annotation
        self.load_zcml_file('configure.zcml', zope.annotation)


COMPONENT_UNIT_TESTING = ComponentUnitTesting()


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

        # Match the mandatory-for-Plone default from plone.recipe.zope2instance
        from Zope2.Startup.datatypes import default_zpublisher_encoding
        default_zpublisher_encoding('utf-8')

        z2.installProduct(app, 'plone.app.versioningbehavior')
        z2.installProduct(app, 'collective.taskqueue.pasplugin')
        z2.installProduct(app, 'Products.CMFPlacefulWorkflow')

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
    name="opengever.core:zserver")


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

    defaultBases = (CACHED_COMPONENT_REGISTRY_ISOLATION, )

    def __init__(self):
        # Keep track of temporary files we create
        self.tempdir = None

        # By super-super-calling the __init__ we remove the SQL bases,
        # since we are implementing SQL setup in this layer directly.
        PloneSandboxLayer.__init__(self)

    def setup_eventlog(self):
        schema = ZConfig.loadSchemaFile(StringIO("""
            <schema>
              <import package='ZConfig.components.logger'/>
              <section type='eventlog' name='*' attribute='eventlog'/>
            </schema>
        """))
        self.tempdir = tempfile.mkdtemp()
        f = open(os.path.join(self.tempdir, 'instance0.log'), 'w')
        f.close()
        eventlog_conf = ZConfig.loadConfigFile(schema, StringIO("""
            <eventlog>
              <logfile>
                path {}
                level debug
              </logfile>
            </eventlog>
        """.format(f.name)))[0]
        assert eventlog_conf.eventlog is not None
        getConfiguration().eventlog = eventlog_conf.eventlog

    def setUpZope(self, app, configurationContext):
        super(ContentFixtureLayer, self).setUpZope(app, configurationContext)

        # Setting up the database, which creates a new engine, must happen after
        # opengever's ZCML is loaded in order to have engine creation event
        # handlers already registered, which enable support for rolling back
        # to savepoints.
        sqlite_testing.setup_memory_database()
        if 'sqlite' in datamanager.NO_SAVEPOINT_SUPPORT:
            datamanager.NO_SAVEPOINT_SUPPORT.remove('sqlite')

        # register bumblebee task queue
        self.bumblebee_queue = BumblebeeTestTaskQueue()
        sm = getSiteManager()
        sm.registerUtility(
            self.bumblebee_queue, provided=ITaskQueue, name='test-queue')

        # provide bumblebee config by default and only deactivate bumblebee
        # with the feature flag.
        os.environ.pop('BUMBLEBEE_DEACTIVATE', None)
        os.environ['BUMBLEBEE_APP_ID'] = 'local'
        os.environ['BUMBLEBEE_SECRET'] = 'secret'
        os.environ['BUMBLEBEE_INTERNAL_PLONE_URL'] = 'http://nohost/plone'
        os.environ['BUMBLEBEE_PUBLIC_URL'] = 'http://bumblebee'

        # Set up ftw.contentstats logging for testing
        self.setup_eventlog()
        setup_logger()

    def setUpPloneSite(self, portal):
        session.current_session = session.BuilderSession()
        session.current_session.session = create_session()
        super(ContentFixtureLayer, self).setUpPloneSite(portal)

        portal.portal_languages.use_combined_language_codes = True
        portal.portal_languages.addSupportedLanguage('de-ch')

        if not DB_CACHE_MANAGER.is_loaded_from_cache(CACHE_GEVER_FIXTURE):
            sqlite_testing.create_tables()
            # Avoid circular imports:
            from opengever.testing.fixtures import OpengeverContentFixture
            setRequest(portal.REQUEST)
            self['fixture_lookup_table'] = OpengeverContentFixture()()
            setRequest(None)
            DB_CACHE_MANAGER.data['fixture_lookup_table'] = (
                self['fixture_lookup_table'])
            DB_CACHE_MANAGER.dump_to_cache(self['zodbDB'], CACHE_GEVER_FIXTURE)
        else:
            DB_CACHE_MANAGER.apply_cache_fixes(CACHE_GEVER_FIXTURE)
            self['fixture_lookup_table'] = (
                DB_CACHE_MANAGER.data['fixture_lookup_table'])

        # bumblebee should only be turned on on-demand with the feature flag.
        # if this assertion fails a profile in the fixture enables bumblebee,
        # or if was left on by mistake after fixture setup.
        assert not is_bumblebee_feature_enabled()

    def installOpengeverProfiles(self, portal):
        if not DB_CACHE_MANAGER.is_loaded_from_cache(CACHE_GEVER_INSTALLATION):
            super(ContentFixtureLayer, self).installOpengeverProfiles(portal)
            DB_CACHE_MANAGER.dump_to_cache(self['zodbDB'], CACHE_GEVER_INSTALLATION)
        else:
            DB_CACHE_MANAGER.apply_cache_fixes(CACHE_GEVER_INSTALLATION)

    def testTearDown(self):
        super(ContentFixtureLayer, self).testTearDown()

        # clear bumblebee queue after each test
        self.bumblebee_queue.reset()

    def tearDownZope(self, app):
        # Clean up ZConf
        conf = getConfiguration()
        del conf.eventlog

    def tearDown(self):
        # Clean up all temporary files we created
        shutil.rmtree(self.tempdir)

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


class GEVERIntegrationTesting(FTWIntegrationTesting):

    def makeSavepoint(self):
        # In order to let the SQL transaction manager make a savepoint of no
        # changes we need to mark the session as changed first.
        mark_changed(create_session())
        return super(GEVERIntegrationTesting, self).makeSavepoint()

    def testSetUp(self):
        super(GEVERIntegrationTesting, self).testSetUp()
        logout()


class ThemeContentFixtureLayer(ContentFixtureLayer):
    """This is a temporary layer that allows to use the ContentFixture
    together with plonetheme.teamraum:gever profile (especially for having
    Diazo transforms applied).

    This is necessary as a separate layer because
    - Using the theme as a FEATURE_PROFILE doesn't seem to work
    - Installing the theme profile in OpengeverFixture's
      installOpengeverProfiles() currently breaks too many existing tests.

    The latter is something we'll eventually want to, but for now this layer
    provides an option to use the fixture together with the theme without
    affecting anything else, and should be rebase-friendly.
    """

    def setUpPloneSite(self, portal):
        super(ThemeContentFixtureLayer, self).setUpPloneSite(portal)
        applyProfile(portal, 'plonetheme.teamraum:gever')


OPENGEVER_INTEGRATION_TESTING_THEME = GEVERIntegrationTesting(
    # Warning: do not try to base other layers on ContentFixtureLayer.
    # See docstring of ContentFixtureLayer.
    bases=(ThemeContentFixtureLayer(), TRAVERSAL_BROWSER_FIXTURE),
    name="opengever.core:theme:integration")


OPENGEVER_INTEGRATION_TESTING = GEVERIntegrationTesting(
    # Warning: do not try to base other layers on ContentFixtureLayer.
    # See docstring of ContentFixtureLayer.
    bases=(ContentFixtureLayer(), TRAVERSAL_BROWSER_FIXTURE),
    name="opengever.core:integration")
