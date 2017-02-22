from collective.taskqueue.interfaces import ITaskQueue
from collective.transmogrifier import transmogrifier
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import session
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import set_builder_session_factory
from ftw.bumblebee.tests.helpers import BumblebeeTestTaskQueue
from ftw.dictstorage.sql import DictStorageModel
from ftw.testing import ComponentRegistryLayer
from ftw.testing.quickinstaller import snapshots
from opengever.activity.interfaces import IActivitySettings
from opengever.base import model
from opengever.base.model import create_session
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings  # noqa
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
from plone.testing.z2 import zopeApp
from Products.CMFCore.utils import getToolByName
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy_utils import create_database
from sqlalchemy_utils import drop_database
from Testing.ZopeTestCase.utils import setupCoreSessions
from z3c.saconfig import EngineFactory
from z3c.saconfig import GloballyScopedSession
from z3c.saconfig.interfaces import IEngineFactory
from z3c.saconfig.interfaces import IScopedSession
from zope.component import getSiteManager
from zope.component import provideUtility
from zope.configuration import xmlconfig
from zope.globalrequest import setRequest
from zope.sqlalchemy import datamanager

import logging
import os
import random
import string
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


class OpengeverFixtureSQL(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

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
        self.allowAllTypes(portal)
        deactivate_activity_center()
        deactivate_bumblebee_feature()

    def tearDown(self):
        clear_transmogrifier_registry()
        super(OpengeverFixtureSQL, self).tearDown()

    def tearDownPloneSite(self, portal):
        activate_activity_center()
        activate_bumblebee_feature()

    def tearDownZope(self, app):
        os.environ['BUMBLEBEE_DEACTIVATE'] = "True"
        super(OpengeverFixtureSQL, self).tearDownZope(app)

    def installOpengeverProfiles(self, portal):
        applyProfile(portal, 'opengever.policy.base:default')
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


OPENGEVER_FIXTURE_SQL = OpengeverFixtureSQL()


class OpengeverFixture(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE_SQL,)

    def testSetUp(self):
        super(OpengeverFixture, self).testSetUp()
        setup_sql_tables()

    def testTearDown(self):
        truncate_sql_tables()
        from opengever.testing.sql import reset_ogds_sync_stamp
        with ploneSite() as portal:
            reset_ogds_sync_stamp(portal)
        super(OpengeverFixture, self).testTearDown()


OPENGEVER_FIXTURE = OpengeverFixture()


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


def functional_session_factory_sql():
    sess = session.BuilderSession()
    # Auto commit must be False to enable matroska rollbacks!
    sess.auto_commit = False
    # We use model.Session here to allow matroskas to switch DB engines in
    # parallel while still allowing ftw.builder to function as intended.
    sess.session = model.Session
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

OPENGEVER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_FIXTURE,
           set_builder_session_factory(integration_session_factory)),
    name="opengever.core:integration")

OPENGEVER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="opengever.core:functional")

OPENGEVER_FUNCTIONAL_TESTING_SQL = FunctionalTesting(
    bases=(OPENGEVER_FIXTURE_SQL,
           set_builder_session_factory(functional_session_factory_sql)),
    name="opengever.core:functional_sql")

OPENGEVER_FUNCTIONAL_ZSERVER_TESTING = FunctionalTesting(
    bases=(z2.ZSERVER_FIXTURE, OPENGEVER_FIXTURE,
           set_builder_session_factory(functional_session_factory),
           ),
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


class SQLTestLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING_SQL,)

    def setUp(self):
        super(SQLTestLayer, self).setUp()

    def setUpPloneSite(self, portal):
        # Grab the parent layer DB
        self.layer_matroska_engine_urls = []
        self.parent_layer_session = model.create_session()
        self.parent_layer_engine = self.parent_layer_session.get_bind()
        self.parent_layer_metadata = MetaData(self.parent_layer_engine)
        # We need to reflect here to get Base vs. BASE vs. DictStorage
        self.parent_layer_metadata.reflect()
        self.parent_layer_tables = self.parent_layer_metadata.sorted_tables

        # Preserve the reference to our parent layer engine or else we cannot
        # properly tear down this layer!

        # Set the parent layer DB as the parent for our first generation
        # matroska.
        self.matroska_parent_session = self.parent_layer_session
        self.matroska_parent_engine = self.parent_layer_engine
        self.matroska_parent_metadata = self.parent_layer_metadata
        self.matroska_parent_tables = self.parent_layer_tables

        # Make our first generation matroska a copy of the parent layer DB
        self.nextMatroska()
        # Seed our first matroska with the layer specific data to be shared
        # across the layer tests.
        self.seedData()

        # Preserve a reference to the seeded first generation matroska so we
        # can make more matroskas based on that and do not have to reseed!
        self.matroska_parent_session = self.current_matroska_session
        self.matroska_parent_engine = self.current_matroska_engine
        self.matroska_parent_metadata = MetaData(self.current_matroska_engine)

        # Generate the first matroska to be actually run tests against
        self.nextMatroska()

    def testSetUp(self):
        super(SQLTestLayer, self).testSetUp()
        # We set up a transaction checkpoint at test setup time in order to
        # check at test teardown time if we can clean up the matroska or not.
        self.savepoint = transaction.savepoint()

    def testTearDown(self):
        # If the transaction cannot be rolled back, we need to roll a new
        # matroska - ZODB gets appropriately rolled back by the normal test
        # isolation mechanisms of the parent layer(s) so we do not have to
        # worry about that.
        if self.savepoint.valid:
            self.savepoint.rollback()
        else:
            self.nextMatroska()

        super(SQLTestLayer, self).testTearDown()

    def tearDown(self):
        # Drop the matroskas we've accumulated
        for url in self.layer_matroska_engine_urls:
            drop_database(url)

        # Switch models back to use the parent layer engine!
        model.Session.bind = self.parent_layer_engine

        # If we have not restored the parent layer engine before we exit here,
        # the underlying layers and further tests will unwantedly try to use
        # whatever matroska engine we last used!
        super(SQLTestLayer, self).tearDown()

    def nextMatroska(self):
        # Create a new database
        self.current_matroska_engine = create_engine(
            'postgresql+psycopg2:///opengever_test_{0}'
            .format(''.join(
                random.choice(string.ascii_lowercase + string.digits)
                for _ in range(8))))

        self.layer_matroska_engine_urls.append(
            self.current_matroska_engine.url)

        create_database(self.current_matroska_engine.url)
        model.Base.metadata.create_all(self.current_matroska_engine)
        BASE.metadata.create_all(self.current_matroska_engine)
        DictStorageModel.metadata.create_all(self.current_matroska_engine)

        self.current_matroska_session = scoped_session(
            sessionmaker(self.current_matroska_engine)())

        # Copy data into our new database from the matroska parent
        for table in self.matroska_parent_tables:
            # Fetch all the data in a table
            data = [dict((column.key, x[column.name])
                         for column in table.c)
                    for x in self.matroska_parent_engine
                    .execute(table.select())]

            # Insert all the data in the table, if any
            if data:
                self.current_matroska_engine.execute(table.insert(), data)

        # Make sure we preserve sequences, if the matroska parent supports them
        if self.matroska_parent_engine.dialect.supports_sequences:
            # Grab parent matroska sequence names
            sequence_names = self.matroska_parent_engine.execute(
                "SELECT c.relname "
                "FROM pg_class c "
                "WHERE c.relkind = 'S'").fetchall()

            for sequence_name in sequence_names:
                # Get the last_value from a parent matroska sequence
                parent_last_value = self.matroska_parent_engine.execute(
                    "SELECT last_value FROM {0}"
                    .format(sequence_name[0])).fetchall()

                # Reset the new matroska sequence to + 1
                # https://www.postgresql.org/docs/current/static/sql-altersequence.html
                self.current_matroska_engine.execute(
                    "ALTER SEQUENCE {0} RESTART WITH {1};"
                    .format(sequence_name[0],
                            parent_last_value[0][0] + 1))

        # Switch DictStorage, Base and BASE to use the per layer engine
        # This works by the virtue of scoped_session being a thread local
        # singleton.
        #
        # This needs to be set back to the parent layer engine at layer
        # teardown or one will suffer very weird artefacts and a debug rabbit
        # hole!
        model.Session.bind = self.current_matroska_engine

    def seedData(self):
        # Circumvent our improper use of ftw.builder
        with zopeApp() as app:
            session.current_session = session.factory()
            setRequest(app.REQUEST)
            setRoles(api.portal.get(),
                     api.user.get_current().id,
                     ['Contributor', 'Editor', 'Reader', 'Member'])

            # Create the layer fixture
            create(Builder('fixture').with_all_unit_setup())
            repository_tree = create(Builder('repository_tree'))
            create(Builder('globalindex_task'))
            create(Builder('globalindex_task').having(int_id=4321))
            create(Builder('task'))
            create(Builder('task'))
            create(Builder('dossier').within(repository_tree[-1]))
            dossier = create(Builder('dossier').within(repository_tree[-1]))
            create(Builder('document').within(dossier))


OPENGEVER_SQL_TEST_LAYER = SQLTestLayer()


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


class DossierTemplateLayer(PloneSandboxLayer):

    def setUpPloneSite(self, portal):
        toggle_feature(IDossierTemplateSettings, enabled=True)

    def tearDownPloneSite(self, portal):
        toggle_feature(IDossierTemplateSettings, enabled=False)

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

    def testTearDown(self):
        self.queue.reset()
        super(BumblebeeLayer, self).testTearDown()

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
