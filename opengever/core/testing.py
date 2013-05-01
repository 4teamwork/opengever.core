from collective.transmogrifier import transmogrifier
from opengever.globalindex import model
from opengever.ogds.base.setuphandlers import create_sql_tables
from opengever.ogds.base.utils import create_session
from opengever.ogds.models import BASE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.testing import z2
from zope.configuration import xmlconfig
from zope.sqlalchemy import datamanager


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


class OpengeverFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # do not install pas plugins (doesnt work in tests)
        from opengever.ogds.base import setuphandlers
        setuphandlers.setup_scriptable_plugin = lambda *a, **kw: None

        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'

            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'

            '  <include package="opengever.ogds.base" file="tests.zcml" />'

            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'plone.app.versioningbehavior')

    def setUpPloneSite(self, portal):
        self.installOpengeverProfiles(portal)
        self.createMemberFolder(portal)
        setup_sql_tables()

    def tearDown(self):
        super(OpengeverFixture, self).tearDown()
        clear_transmogrifier_registry()

    def installOpengeverProfiles(self, portal):
        # Copied from metadata.zxml of opengever.policy.base:default
        # The aim is to use the opengever.policy.base:default here, but it
        # changes some things such as the language which will result in
        # lots of failing tests.
        applyProfile(portal, 'opengever.globalindex:default')
        applyProfile(portal, 'opengever.base:default')
        applyProfile(portal, 'opengever.document:default')
        applyProfile(portal, 'opengever.dossier:default')
        applyProfile(portal, 'opengever.repository:default')
        applyProfile(portal, 'opengever.journal:default')
        applyProfile(portal, 'opengever.task:default')
        applyProfile(portal, 'opengever.inbox:default')
        applyProfile(portal, 'opengever.tabbedview:default')
        applyProfile(portal, 'opengever.tasktemplates:default')
        applyProfile(portal, 'opengever.portlets.tree:default')
        applyProfile(portal, 'opengever.trash:default')
        applyProfile(portal, 'opengever.ogds.base:default')
        applyProfile(portal, 'opengever.contact:default')
        applyProfile(portal, 'opengever.advancedsearch:default')
        applyProfile(portal, 'opengever.sharing:default')
        applyProfile(portal, 'opengever.latex:default')
        applyProfile(portal, 'ftw.datepicker:default')
        applyProfile(portal, 'izug.basetheme:opengever')
        applyProfile(portal, 'plone.formwidget.autocomplete:default')
        applyProfile(portal, 'plone.formwidget.contenttree:default')

    def createMemberFolder(self, portal):
        # Create a Members folder.
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory('Folder', 'Members')
        portal['Members'].invokeFactory('Folder', TEST_USER_ID)
        setRoles(portal, TEST_USER_ID, ['Member'])


OPENGEVER_FIXTURE = OpengeverFixture()

OPENGEVER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_FIXTURE, ), name="opengever.core:integration")

OPENGEVER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_FIXTURE, ), name="opengever.core:functional")
