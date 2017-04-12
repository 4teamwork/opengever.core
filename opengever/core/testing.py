from collective.taskqueue.interfaces import ITaskQueue
from collective.transmogrifier import transmogrifier
from ftw.builder import session
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import set_builder_session_factory
from ftw.bumblebee.tests.helpers import BumblebeeTestTaskQueue
from ftw.testing import ComponentRegistryLayer
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from ftw.testing.quickinstaller import snapshots
from opengever.activity.interfaces import IActivitySettings
from opengever.base.model import create_session
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
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.browserlayer.utils import unregister_layer
from plone.dexterity.schema import SCHEMA_CACHE
from plone.testing import z2
from Products.CMFCore.utils import getToolByName
from Testing.ZopeTestCase.utils import setupCoreSessions
from zope.component import getSiteManager
from zope.configuration import xmlconfig
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

    def __init__(self, sql_layer):
        bases = self.defaultBases + (sql_layer, )
        name = ':'.join((self.__class__.__name__,
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

            '  <include package="opengever.core.tests" file="tests.zcml" />'
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
    sqlite_testing.SQLITE_MEMORY_FIXTURE)

# OPENGEVER_FIXTURE is the default fixture used in policy tests.
OPENGEVER_FIXTURE = OPENGEVER_FIXTURE_SQLITE

OPENGEVER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_FIXTURE_SQLITE,
           set_builder_session_factory(integration_session_factory)),
    name="opengever.core:integration")

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
