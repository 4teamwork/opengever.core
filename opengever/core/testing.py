from collective.transmogrifier import transmogrifier
from ftw.builder import session
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import set_builder_session_factory
from ftw.testing import ComponentRegistryLayer
from opengever.core.tests import patches
from opengever.globalindex import model
from opengever.ogds.base.setup import create_sql_tables
from opengever.ogds.base.utils import create_session
from opengever.ogds.models import BASE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import ploneSite
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.browserlayer.utils import unregister_layer
from plone.dexterity.schema import SCHEMA_CACHE
from plone.testing import Layer
from plone.testing import z2
from Products.CMFCore.utils import getToolByName
from Testing.ZopeTestCase.utils import setupCoreSessions
from z3c.saconfig import EngineFactory
from z3c.saconfig import GloballyScopedSession
from z3c.saconfig.interfaces import IEngineFactory
from z3c.saconfig.interfaces import IScopedSession
from zope.component import provideUtility
from zope.configuration import xmlconfig
from zope.sqlalchemy import datamanager
import transaction


patches.disable_quickinstaller_snapshots()


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

            '  <include package="opengever.ogds.base" file="tests.zcml" />'
            '  <include package="opengever.setup.tests" />'

            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'plone.app.versioningbehavior')

        setupCoreSessions(app)

        # Set max subobject limit to 0 -> unlimited
        # In tests this is set to 100 by default
        transient_object_container = app.temp_folder.session_data
        transient_object_container.setSubobjectLimit(0)

    def setUpPloneSite(self, portal):
        self.installOpengeverProfiles(portal)
        self.createMemberFolder(portal)

    def tearDown(self):
        super(OpengeverFixture, self).tearDown()
        clear_transmogrifier_registry()

    def installOpengeverProfiles(self, portal):
        # Copied from metadata.zxml of opengever.policy.base:default
        # The aim is to use the opengever.policy.base:default here, but it
        # changes some things such as the language which will result in
        # lots of failing tests.
        applyProfile(portal, 'plone.app.dexterity:default')
        applyProfile(portal, 'plone.app.registry:default')
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
        applyProfile(portal, 'ftw.datepicker:default')
        applyProfile(portal, 'plone.formwidget.autocomplete:default')
        applyProfile(portal, 'plone.formwidget.contenttree:default')
        applyProfile(portal, 'ftw.contentmenu:default')

    def createMemberFolder(self, portal):
        # Create a Members folder.
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory('Folder', 'Members')
        portal['Members'].invokeFactory('Folder', TEST_USER_ID)
        setRoles(portal, TEST_USER_ID, ['Member'])


class MemoryDBLayer(Layer):
    """A Layer which only set up a test sqlite db in to the memory
    """

    def testSetUp(self):
        super(MemoryDBLayer, self).testSetUp()
        setup_sql_tables()
        self.session = create_session()

    def testTearDown(test):
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
    engine_factory = EngineFactory('sqlite:///:memory:')
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
