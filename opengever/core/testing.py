from collective.taskqueue.interfaces import ITaskQueue
from collective.transmogrifier import transmogrifier
from ftw.builder import session
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import set_builder_session_factory
from ftw.bumblebee.tests.helpers import BumblebeeTestTaskQueue
from ftw.testing import ComponentRegistryLayer
from ftw.testing.quickinstaller import snapshots
from opengever.activity.interfaces import IActivitySettings
from opengever.base import model
from opengever.base.model import create_session
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.meeting.interfaces import IMeetingSettings
from opengever.officeatwork.interfaces import IOfficeatworkSettings
from opengever.ogds.base.setup import create_sql_tables
from opengever.ogds.models import BASE
from opengever.private import enable_opengever_private
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PLONE_ZSERVER
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import ploneSite
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.browserlayer.utils import unregister_layer
from plone.dexterity.schema import SCHEMA_CACHE
from plone.testing import Layer
from plone.testing import z2
from Products.CMFCore.utils import getToolByName
from sqlalchemy.pool import StaticPool
from Testing.ZopeTestCase.utils import setupCoreSessions
from z3c.saconfig import EngineFactory
from z3c.saconfig import GloballyScopedSession
from z3c.saconfig.interfaces import IEngineFactory
from z3c.saconfig.interfaces import IScopedSession
from zope.component import getSiteManager
from zope.component import provideUtility
from zope.configuration import xmlconfig
from zope.sqlalchemy import datamanager
import logging
import os
import sys
import transaction


loghandler = logging.StreamHandler(stream=sys.stdout)
loghandler.setLevel(logging.DEBUG)
for name, level in {'plone.protect': logging.INFO,
                    'opengever.base.protect': logging.INFO}.items():
    logger = logging.getLogger(name)
    logger.addHandler(loghandler)
    logger.setLevel(level)


snapshots.disable()


def clear_transmogrifier_registry():
    transmogrifier.configuration_registry._config_info = {}
    transmogrifier.configuration_registry._config_ids = []


def setup_sql_tables():
    # Create opengever.ogds.base SQL tables
    create_sql_tables()

    # Create opengever.globalindex SQL tables
    model.Base.metadata.create_all(create_session().bind)

    # Activate savepoint "support" for sqlite
    # We need savepoint support for version retrieval with CMFEditions.
    if 'sqlite' in datamanager.NO_SAVEPOINT_SUPPORT:
        datamanager.NO_SAVEPOINT_SUPPORT.remove('sqlite')


def truncate_sql_tables():
    tables = BASE.metadata.tables.values() + \
        model.Base.metadata.tables.values()

    session = create_session()

    for table in tables:
        session.execute(table.delete())


def toggle_feature(registry_interface, enabled=True):

    api.portal.set_registry_record('is_feature_enabled', enabled,
                                   interface=registry_interface)
    transaction.commit()


def deactivate_meeting():
    toggle_feature(IMeetingSettings, enabled=False)


def activate_meeting():
    toggle_feature(IMeetingSettings, enabled=True)


def deactivate_activity_center():
    toggle_feature(IActivitySettings, enabled=False)


def activate_activity_center():
    toggle_feature(IActivitySettings, enabled=True)


def activate_officeatwork():
    toggle_feature(IOfficeatworkSettings, enabled=True)


def deactivate_officeatwork():
    toggle_feature(IOfficeatworkSettings, enabled=False)


def deactivate_bumblebee_feature():
    toggle_feature(IGeverBumblebeeSettings, enabled=False)


def activate_bumblebee_feature():
    toggle_feature(IGeverBumblebeeSettings, enabled=True)


class AnnotationLayer(ComponentRegistryLayer):
    """Loads ZML of zope.annotation.
    """

    def setUp(self):
        super(AnnotationLayer, self).setUp()
        import zope.annotation
        self.load_zcml_file('configure.zcml', zope.annotation)


ANNOTATION_LAYER = AnnotationLayer()


class OpengeverFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def testSetUp(self):
        super(OpengeverFixture, self).testSetUp()
        setup_sql_tables()

    def testTearDown(self):
        truncate_sql_tables()
        from opengever.testing.sql import reset_ogds_sync_stamp
        with ploneSite() as portal:
            reset_ogds_sync_stamp(portal)
        super(OpengeverFixture, self).testTearDown()

    def setUpZope(self, app, configurationContext):
        # do not install pas plugins (doesnt work in tests)
        from opengever.ogds.base import hooks
        hooks._setup_scriptable_plugin = lambda *a, **kw: None

        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'

            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'

            '  <include package="opengever.core.tests" file="tests.zcml" />'
            '  <include package="opengever.ogds.base" file="tests.zcml" />'
            '  <include package="opengever.base.tests" file="tests.zcml" />'
            '  <include package="opengever.testing" file="tests.zcml" />'
            '  <include package="opengever.setup.tests" />'

            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'plone.app.versioningbehavior')
        z2.installProduct(app, 'collective.taskqueue.pasplugin')

        memory_session_factory()
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
        deactivate_activity_center()
        deactivate_bumblebee_feature()

    def tearDown(self):
        super(OpengeverFixture, self).tearDown()
        clear_transmogrifier_registry()

    def tearDownPloneSite(self, portal):
        activate_activity_center()
        activate_bumblebee_feature()

    def tearDownZope(self, app):
        super(OpengeverFixture, self).tearDownZope(app)
        os.environ['BUMBLEBEE_DEACTIVATE'] = "True"

    def installOpengeverProfiles(self, portal):
        # Copied from metadata.zxml of opengever.policy.base:default
        # The aim is to use the opengever.policy.base:default here, but it
        # changes some things such as the language which will result in
        # lots of failing tests.
        applyProfile(portal, 'plone.app.dexterity:default')
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'plone.app.relationfield:default')
        applyProfile(portal, 'opengever.globalindex:default')
        applyProfile(portal, 'opengever.ogds.base:default')
        applyProfile(portal, 'opengever.base:default')
        applyProfile(portal, 'opengever.document:default')
        applyProfile(portal, 'opengever.mail:default')
        applyProfile(portal, 'opengever.dossier:default')
        applyProfile(portal, 'opengever.repository:default')
        applyProfile(portal, 'opengever.journal:default')
        applyProfile(portal, 'opengever.task:default')
        applyProfile(portal, 'opengever.tabbedview:default')
        applyProfile(portal, 'opengever.trash:default')
        applyProfile(portal, 'opengever.inbox:default')
        applyProfile(portal, 'opengever.tasktemplates:default')
        applyProfile(portal, 'opengever.portlets.tree:default')
        applyProfile(portal, 'opengever.contact:default')
        applyProfile(portal, 'opengever.advancedsearch:default')
        applyProfile(portal, 'opengever.sharing:default')
        applyProfile(portal, 'opengever.latex:default')
        applyProfile(portal, 'opengever.meeting:default')
        applyProfile(portal, 'opengever.activity:default')
        applyProfile(portal, 'opengever.bumblebee:default')
        applyProfile(portal, 'opengever.officeatwork:default')
        applyProfile(portal, 'opengever.private:default')
        applyProfile(portal, 'ftw.datepicker:default')
        applyProfile(portal, 'plone.formwidget.autocomplete:default')
        applyProfile(portal, 'plone.formwidget.contenttree:default')
        applyProfile(portal, 'ftw.contentmenu:default')
        applyProfile(portal, 'ftw.zipexport:default')
        applyProfile(portal, 'opengever.disposition:default')

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

        For production, the language tool is configured in
        opengever.policy.base:default, which we don't import here
        (see comment in installOpengeverProfiles() above).
        """
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.use_combined_language_codes = True
        lang_tool.display_flags = False
        lang_tool.start_neutral = False
        lang_tool.use_subdomain_negotiation = False
        lang_tool.authenticated_users_only = False
        lang_tool.use_request_negotiation = True

        # These would be (possible) production defaults, but will break tests
        # lang_tool.setDefaultLanguage('de-ch')
        # lang_tool.supported_langs = ['fr-ch', 'de-ch']


class APILayer(Layer):
    """A layer that installs the plone.restapi:default generic setup profile.
    """

    def setUp(self):
        with ploneSite() as site:
            applyProfile(site, 'plone.restapi:default')


RESTAPI_LAYER = APILayer()


class MemoryDBLayer(Layer):
    """A Layer which only set up a test sqlite db in to the memory
    """

    def testSetUp(self):
        super(MemoryDBLayer, self).testSetUp()
        setup_sql_tables()
        self.session = create_session()

    def testTearDown(self):
        truncate_sql_tables()
        transaction.abort()


def integration_session_factory():
    sess = session.BuilderSession()
    sess.session = create_session()
    return sess


def functional_session_factory():
    sess = session.BuilderSession()
    sess.auto_commit = True
    sess.session = create_session()
    return sess


def memory_session_factory():
    engine_factory = EngineFactory(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool)
    provideUtility(
        engine_factory, provides=IEngineFactory, name=u'opengever_db')

    scoped_session = GloballyScopedSession(engine=u'opengever_db')
    provideUtility(
        scoped_session, provides=IScopedSession, name=u'opengever')

    return functional_session_factory()


MEMORY_DB_LAYER = MemoryDBLayer(
    bases=(BUILDER_LAYER,
           set_builder_session_factory(memory_session_factory)),
    name='opengever:core:memory_db')

OPENGEVER_FIXTURE = OpengeverFixture()

OPENGEVER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_FIXTURE,
           set_builder_session_factory(integration_session_factory)),
    name="opengever.core:integration")

OPENGEVER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="opengever.core:functional")

OPENGEVER_FUNCTIONAL_ZSERVER_TESTING = FunctionalTesting(
    bases=(z2.ZSERVER_FIXTURE, OPENGEVER_FIXTURE,
           set_builder_session_factory(functional_session_factory),
           ),
    name="opengever.core:functional:zserver")

OPENGEVER_FUNCTIONAL_ZSERVER_API_TESTING = FunctionalTesting(
    bases=(OPENGEVER_FIXTURE,
           RESTAPI_LAYER,
           set_builder_session_factory(functional_session_factory),
           PLONE_ZSERVER),
    name="opengever.core:functional:zserver:api")


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

    def tearDownPloneSite(self, portal):
        inactivate_filing_number(portal)

OPENGEVER_FUNCTIONAL_FILING_LAYER = FilingLayer()


class MeetingLayer(PloneSandboxLayer):

    def setUpPloneSite(self, portal):
        activate_meeting()

    def tearDownPloneSite(self, portal):
        deactivate_meeting()

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING,)


OPENGEVER_FUNCTIONAL_MEETING_LAYER = MeetingLayer()


class ActivityLayer(PloneSandboxLayer):

    def setUpPloneSite(self, portal):
        activate_activity_center()

    def tearDownPloneSite(self, portal):
        deactivate_activity_center()

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING,)


OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER = ActivityLayer()


class BumblebeeLayer(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        super(BumblebeeLayer, self).setUpZope(app, configurationContext)

        queue = BumblebeeTestTaskQueue()
        sm = getSiteManager()
        sm.registerUtility(queue, provided=ITaskQueue, name='test-queue')

    def setUpPloneSite(self, portal):
        activate_bumblebee_feature()

    def tearDownPloneSite(self, portal):
        deactivate_bumblebee_feature()

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

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING,)


OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER = BumblebeeLayer()


class PrivateFolderLayer(PloneSandboxLayer):

    def setUpPloneSite(self, portal):
        enable_opengever_private()

    def tearDownPloneSite(self, portal):
        mtool = api.portal.get_tool('portal_membership')
        if mtool.getMemberareaCreationFlag():
            mtool.setMemberareaCreationFlag()

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING,)


OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER = PrivateFolderLayer()


class OfficeatworkLayer(PloneSandboxLayer):

    def setUpPloneSite(self, portal):
        activate_officeatwork()

    def tearDownPloneSite(self, portal):
        deactivate_officeatwork()

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING,)


OPENGEVER_FUNCTIONAL_OFFICEATWORK_LAYER = OfficeatworkLayer()
