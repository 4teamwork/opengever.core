from contextlib import contextmanager
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import session
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.testing import freeze
from ftw.testing import staticuid
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from opengever.base.interfaces import ISearchSettings
from opengever.base.model import create_session
from opengever.base.tests.test_config_checks import DummyCheckMissconfigured1
from opengever.core import sqlite_testing
from opengever.core.docker_testing import RedisServiceLayer
from opengever.core.docker_testing import SablonServiceLayer
from opengever.core.solr_testing import SolrReplicationAPIClient
from opengever.core.solr_testing import SolrServer
from opengever.core.testing import activate_bumblebee_feature
from opengever.core.testing import OpengeverFixture
from opengever.core.testserver_zope2server import ISOLATION_READINESS
from opengever.dossier.interfaces import IDossierType
from opengever.sign.pending_signing_job import PendingSigningJob
from opengever.sign.signed_version import SignedVersions
from opengever.testing.helpers import incrementing_intids
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.testing import z2
from requests.exceptions import ConnectionError
from uuid import uuid4
from zope.component import getGlobalSiteManager
from zope.component import getSiteManager
from zope.configuration import xmlconfig
from zope.globalrequest import setRequest
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import atexit
import imp
import opengever.sign.client
import os
import pytz
import transaction


SOLR_HOSTNAME = os.environ.get('SOLR_HOSTNAME', 'localhost')
SOLR_PORT = os.environ.get('SOLR_PORT', '55003')
SOLR_CORE = os.environ.get('SOLR_CORE', 'testserver')
REUSE_RUNNING_SOLR = os.environ.get('TESTSERVER_REUSE_RUNNING_SOLR', None)

opengever.sign.client.sign_service_client = opengever.sign.client.NullSignServiceClient()


class SQLiteBackup(object):
    backup_data = ''

    def isolate(self):
        if self.backup_data:
            self.restore()
        else:
            self.backup()

    def backup(self):
        for line in create_session().bind.raw_connection().connection.iterdump():
            # We only want to store sql statements of the
            # DML (Data Manipulation Language). Thus, we skip all other statements.
            #
            # When we restore the data in the restore-function, we'll empty all
            # tables and feed it with the backedup data.
            if 'CREATE TABLE' in line or \
               'opengever_upgrade_version' in line or \
               'CREATE INDEX' in line:
                continue
            self.backup_data += line

    def restore(self):
        sqlite_testing.truncate_tables()
        create_session().bind.raw_connection().connection.executescript(self.backup_data)


sqlite_backup = SQLiteBackup()
redis_service_layer = RedisServiceLayer()


def default_fixture_class():
    from opengever.testing.fixtures import OpengeverContentFixture

    class OpengeverContentFixtureTestserver(OpengeverContentFixture):
        def create_fixture_content(self):
            super(OpengeverContentFixtureTestserver, self).create_fixture_content()

            with self.freeze_at_hour(20):
                with self.login(self.dossier_responsible):
                    self.create_signing_dossier()

        @staticuid()
        def create_signing_dossier(self):
            self.signing_dossier = self.register('signing_dossier', create(
                Builder('dossier')
                .within(self.repofolder00)
                .titled(u'Signieren')
                .having(
                    description=u'Signierte Dokumente.',
                    responsible=self.dossier_responsible.getId(),
                )
            ))

            self.pending_signing_document = self.register('pending_signing_document', create(
                Builder('document')
                .within(self.signing_dossier)
                .titled(u'Zu signierendes Dokument')
                .in_state('document-state-signing')
                .attach_file_containing(
                    bumblebee_asset('example.docx').bytes(),
                    u'contract.docx')
                .pending_signing_job(
                    PendingSigningJob.from_json_object({
                        'userid': self.dossier_responsible.getId(),
                        'editors': [{'email': 'robert.ziegler@gever.local'}],
                        'signatures': [
                            {
                                'email': 'robert.ziegler@gever.local',
                                'status': 'open',
                            },
                            {
                                'email': 'signed@example.com',
                                'status': 'signed',
                                'signed_at': '2025-01-28T15:00:00.000Z',
                            },
                            {
                                'email': 'declined@example.com',
                                'status': 'declined',
                            }
                        ]
                    })
                )
            ))

            self.signed_document = self.register('signed_document', create(
                Builder('document')
                .within(self.signing_dossier)
                .titled(u'Signiertes Dokument')
                .in_state('document-state-signed')
                .attach_file_containing(
                    bumblebee_asset('example.docx').bytes(),
                    u'contract.docx')
                .signed_versions(SignedVersions.from_json_object(
                    {
                        1: {
                            'id': 1,
                            'created': u'2024-02-18T15:45:00',
                            'signatories': [
                                {
                                    'email': 'robert.ziegler@gever.local',
                                    'userid': 'nicole.kohler',
                                    'signed_at': '2025-01-28T15:00:00.000Z',
                                }
                            ],
                            'version': 1
                        },
                        3: {
                            'id': 3,
                            'created': u'2025-02-18T15:45:00',
                            'signatories': [
                                {
                                    'email': 'robert.ziegler@gever.local',
                                    'userid': 'nicole.kohler',
                                    'signed_at': '2025-01-29T15:00:00.000Z',
                                },
                                {
                                    'email': 'signed@example.com',
                                    'userid': '',
                                    'signed_at': '2025-01-30T15:00:00.000Z',
                                }
                            ],
                            'version': 3
                        }
                    },
                ))
            ))

    return OpengeverContentFixtureTestserver


class TestserverLayer(OpengeverFixture):
    defaultBases = (COMPONENT_REGISTRY_ISOLATION,)

    def setUpZope(self, app, configurationContext):
        ISOLATION_READINESS.patch_publisher()
        solr = SolrServer.get_instance()
        solr.configure(SOLR_PORT, SOLR_CORE, hostname=SOLR_HOSTNAME)
        SolrReplicationAPIClient.get_instance().configure(SOLR_PORT, SOLR_CORE, SOLR_HOSTNAME)

        try:
            solr.is_ready()

            if REUSE_RUNNING_SOLR != SOLR_PORT:
                raise Exception(
                    "There is already a running solr on port {}. "
                    "Run the script with 'TESTSERVER_REUSE_RUNNING_SOLR={} bin/testserver'"
                    " to reuse the running solr instance.".format(SOLR_PORT, SOLR_PORT))
            print 'Using already running solr on port {}'.format(SOLR_PORT)
        except ConnectionError:
            if SOLR_HOSTNAME != 'localhost' and REUSE_RUNNING_SOLR:
                raise Exception('Solr is not reachable at {}:{}'.format(
                    SOLR_HOSTNAME, REUSE_RUNNING_SOLR))

            print 'Starting solr on port {}'.format(SOLR_PORT)
            solr.start()

        import collective.indexing.monkey  # noqa
        import ftw.solr.patches  # noqa

        super(TestserverLayer, self).setUpZope(app, configurationContext)

        # Solr must be started before registering the connection since ftw.solr
        # will get the schema from solr and cache it.
        solr.await_ready()

        xmlconfig.string(
            '<configure xmlns:solr="http://namespaces.plone.org/solr">'
            '  <solr:connection host="{SOLR_HOSTNAME}"'
            '                   port="{SOLR_PORT}"'
            '                   base="/solr/{SOLR_CORE}"'
            '                   upload_blobs="true"/>'
            '</configure>'.format(SOLR_HOSTNAME=SOLR_HOSTNAME,
                                  SOLR_PORT=SOLR_PORT,
                                  SOLR_CORE=SOLR_CORE),
            context=configurationContext)

        # Clear solr from potential artefacts of the previous run.
        SolrReplicationAPIClient.get_instance().clear()

        # Start our own Sablon service if we didn't get a Sablon URL.
        if not os.environ.get('SABLON_URL'):
            sablon = SablonServiceLayer()
            sablon.setUp()
            atexit.register(sablon.tearDown)

        redis_service_layer.setUp()
        atexit.register(redis_service_layer.tearDown)

        # Install a Virtual Host Monster
        if "virtual_hosting" not in app.objectIds():
            # If ZopeLite was imported, we have no default virtual
            # host monster
            from Products.SiteAccess.VirtualHostMonster import (
                manage_addVirtualHostMonster,
            )

            manage_addVirtualHostMonster(app, "virtual_hosting")

    def setUpPloneSite(self, portal):
        session.current_session = session.BuilderSession()
        session.current_session.session = create_session()
        super(TestserverLayer, self).setUpPloneSite(portal)

        applyProfile(portal, 'plonetheme.teamraum:gever')

        portal.portal_languages.use_combined_language_codes = True
        portal.portal_languages.addSupportedLanguage('de-ch')

        # Disable secure session cookie as tests are run without HTTPS
        portal.acl_users['session'].secure = False

        api.portal.set_registry_record('use_solr', True, interface=ISearchSettings)
        activate_bumblebee_feature()

        self.replaceDossierTypesVocabulary()

        # Register a broken configuration-check
        getSiteManager().registerAdapter(DummyCheckMissconfigured1, name="check-missconfigured-1")

        setRequest(portal.REQUEST)
        print 'Installing fixture. Have patience.'
        self.get_fixture_class()()
        print 'Finished installing fixture.'
        setRequest(None)

        # Commit before creating the solr backup, since collective.indexing
        # flushes on commit.
        transaction.commit()

        # The solr backup API allows creating named backup, but not removing them
        # nor overwriting existing backups.
        if SOLR_HOSTNAME == 'localhost':
            # When solr runs on the same system we can remove backups from the disk.
            # By doing that we can make sure that we are not blowing up the disk
            # with old solr backups.
            self['solr_backup_name'] = 'testserver-fixture'
        else:
            # When solr runs on another host (e.g. within docker), we cannot easily
            # access its disk. So we need to create uniquely named backups and we
            # cannot clean it up because the API has no such endpoint.
            self['solr_backup_name'] = 'testserver-{}'.format(str(uuid4()))

        SolrReplicationAPIClient.get_instance().create_backup(self['solr_backup_name'])

    def setupLanguageTool(self, portal):
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de')
        lang_tool.supported_langs = ['de-ch', 'fr-ch']

    def replaceDossierTypesVocabulary(self):
        """Register testserver-specific dossier-types.
        It does not work with overrides.zcml for testserver only. So we have to do it manually
        """
        def dossier_types_vocabulary_factory(context):
            return SimpleVocabulary([
                SimpleTerm('businesscase', title=u'Gesch\xe4ftsfall'),
                SimpleTerm('project', title='Projektdossier')
            ])

        utility_name = 'opengever.dossier.dossier_types'
        gsm = getGlobalSiteManager()
        gsm.unregisterUtility(provided=IVocabularyFactory, name=utility_name)
        gsm.registerUtility(dossier_types_vocabulary_factory, provided=IVocabularyFactory, name=utility_name)

        # Do not hide the initial dossier_type.
        api.portal.set_registry_record(
            name='hidden_dossier_types', interface=IDossierType, value=[])

    def get_fixture_class(self):
        """The fixture of the testserver should be replaceable from the outside.
        The idea is that the 'FIXTURE' environment variable can be set to a path
        to a python file which is located in another project.
        Therefore we import the file manually in the context of GEVER so that
        subclassing the fixture works.
        """
        custom_fixture_path = os.environ.get('FIXTURE', None)

        if not custom_fixture_path:
            return default_fixture_class()

        fixture_dir = os.path.dirname(custom_fixture_path)
        package_name = 'customfixture'
        module_name = os.path.splitext(os.path.basename(custom_fixture_path))[0]
        module_path = '{}.{}'.format(package_name, module_name)

        # It is important to first load the package of the custom fixture, so that
        # local imports will work within this package.
        imp.load_module(package_name, *imp.find_module('.', [fixture_dir]))
        module = imp.load_module(module_path, *imp.find_module(module_name, [fixture_dir]))
        class_name = os.environ.get('FIXTURE_CLASS', 'Fixture')
        klass = getattr(module, class_name, None)
        assert klass, 'Could not find class {!r} in module {!r}'.format(class_name, module)
        return klass


class TestServerFunctionalTesting(FunctionalTesting):

    @contextmanager
    def isolation(self):
        start = datetime(2018, 11, 22, 14, 29, 33, tzinfo=pytz.UTC)
        with freeze(start, ignore_modules=['ftw.tokenauth.oauth2.jwt_grants']):
            with staticuid('testserver-session'):
                with incrementing_intids():
                    yield

    def testSetUp(self):
        super(TestServerFunctionalTesting, self).testSetUp()
        self.context_manager = self.isolation()
        self.context_manager.__enter__()

        sqlite_backup.isolate()
        redis_service_layer.testSetUp()
        transaction.commit()

    def testTearDown(self):
        self.context_manager.__exit__(None, None, None)
        SolrReplicationAPIClient.get_instance().restore_backup(self['solr_backup_name'])
        SolrReplicationAPIClient.get_instance().await_restored()
        super(TestServerFunctionalTesting, self).testTearDown()


OPENGEVER_TESTSERVER = TestServerFunctionalTesting(
    bases=(TestserverLayer(), z2.ZSERVER_FIXTURE),
    name="opengever.core:testserver")
