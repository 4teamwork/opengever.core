from alembic.migration import MigrationContext
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.classification import public_trial_default
from opengever.base.default_values import get_persisted_value_for_field
from opengever.base.default_values import object_has_value_for_field
from opengever.core.upgrade import DefaultValuePersister
from opengever.core.upgrade import IdempotentOperations
from opengever.core.upgrade import IntIdMaintenanceJobContextManagerMixin
from opengever.core.upgrade import NightlyIndexer
from opengever.core.upgrade import NightlyWorkflowSecurityUpdater
from opengever.core.upgrade import UIDMaintenanceJobContextManagerMixin
from opengever.nightlyjobs.maintenance_jobs import MaintenanceJobType
from opengever.nightlyjobs.runner import NightlyJobRunner
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
from plone.uuid.interfaces import IUUID
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.engine.reflection import Inspector
from unittest import TestCase
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestIdempotentOperations(TestCase):
    """Test database migration utilities.

    Unfortunately not all operations can be tested with an SQLite database
    since not all ALTER TABLE operations are supported, see
    http://www.sqlite.org/lang_altertable.html.

    Currenlty these untested operations are:
    - IdempotentOperations. drop_column
    - DeactivatedFKConstraint

    """
    def setUp(self):
        self.connection = create_engine('sqlite:///:memory:').connect()
        self.metadata = MetaData(self.connection)
        self.table = Table('thingy', self.metadata,
                           Column('thingy_id', Integer, primary_key=True))
        self.metadata.create_all()

        self.migration_context = MigrationContext.configure(self.connection)
        self.op = IdempotentOperations(self.migration_context, self.metadata)
        self.inspector = Inspector(self.connection)

    def tearDown(self):
        self.metadata.drop_all()
        self.connection.close()

    def refresh_metadata(self):
        self.metadata.clear()
        self.metadata.reflect()

    def test_add_column_works_with_valid_preconditions(self):
        self.assertEqual(['thingy_id'],
                         self.metadata.tables['thingy'].columns.keys())

        self.op.add_column('thingy', Column('foo', String))
        self.refresh_metadata()

        self.assertEqual(['thingy_id', 'foo'],
                         self.metadata.tables['thingy'].columns.keys())

    def test_add_column_skips_add_when_column_name_already_exists(self):
        self.assertEqual(['thingy_id'],
                         self.metadata.tables['thingy'].columns.keys())

        self.op.add_column('thingy', Column('thingy_id', String))
        self.refresh_metadata()

        self.assertEqual(['thingy_id'],
                         self.metadata.tables['thingy'].columns.keys())

    def test_create_tables_skips_create_when_table_already_exists(self):
        self.assertEqual(['thingy'], self.metadata.tables.keys())

        self.op.create_table('thingy')
        self.refresh_metadata()
        self.assertEqual(['thingy'], self.metadata.tables.keys())

    def test_create_table_works_with_valid_preconditions(self):
        self.assertEqual(['thingy'], self.metadata.tables.keys())
        self.op.create_table('xuq', Column('foo', Integer, primary_key=True))
        self.refresh_metadata()
        self.assertEqual(['thingy', 'xuq'], self.metadata.tables.keys())


class DummyIntIdMaintenanceJobManager(IntIdMaintenanceJobContextManagerMixin):

    @property
    def job_type(self):
        function_dotted_name = ".".join((self.__module__,
                                         self.__class__.__name__,
                                         self.dummy_function.__name__))
        return MaintenanceJobType(function_dotted_name)

    @staticmethod
    def dummy_function(key):
        return


class TestIntIdMaintenanceJobContextManagerMixins(IntegrationTestCase):

    def test_add_by_obj(self):
        self.login(self.manager)
        job_manager = DummyIntIdMaintenanceJobManager()

        self.assertEqual(0, job_manager.queue_manager.get_jobs_count())

        with job_manager:
            job_manager.add_by_obj(self.dossier)

        self.assertEqual(1, job_manager.queue_manager.get_jobs_count())
        job = tuple(job_manager.queue_manager.jobs)[0]
        intid = getUtility(IIntIds).getId(self.dossier)
        self.assertEqual(intid, job.variable_argument)
        self.assertEqual(self.dossier,
                         job_manager.key_to_obj(job.variable_argument))


class DummyUIDMaintenanceJobManager(UIDMaintenanceJobContextManagerMixin):

    @property
    def job_type(self):
        function_dotted_name = ".".join((self.__module__,
                                         self.__class__.__name__,
                                         self.dummy_function.__name__))
        return MaintenanceJobType(function_dotted_name)

    @staticmethod
    def dummy_function(key):
        return


class TestUIDMaintenanceJobContextManagerMixins(IntegrationTestCase):

    def test_add_by_obj(self):
        self.login(self.manager)
        job_manager = DummyUIDMaintenanceJobManager()

        self.assertEqual(0, job_manager.queue_manager.get_jobs_count())

        with job_manager:
            job_manager.add_by_obj(self.dossier)

        self.assertEqual(1, job_manager.queue_manager.get_jobs_count())
        job = tuple(job_manager.queue_manager.jobs)[0]
        self.assertEqual(self.dossier.UID(), job.variable_argument)
        self.assertEqual(self.dossier,
                         job_manager.key_to_obj(job.variable_argument))

    def test_add_by_brain(self):
        self.login(self.manager)
        job_manager = DummyUIDMaintenanceJobManager()

        self.assertEqual(0, job_manager.queue_manager.get_jobs_count())

        with job_manager:
            job_manager.add_by_brain(obj2brain(self.dossier))

        self.assertEqual(1, job_manager.queue_manager.get_jobs_count())
        job = tuple(job_manager.queue_manager.jobs)[0]
        self.assertEqual(self.dossier.UID(), job.variable_argument)
        self.assertEqual(self.dossier,
                         job_manager.key_to_obj(job.variable_argument))


class TestNightlyIndexer(SolrIntegrationTestCase):

    def run_nightly_jobs(self):
        runner = NightlyJobRunner(force_execution=True)
        runner.execute_pending_jobs()
        self.commit_solr()

    def assert_catalog_data(self, obj, idx, value):
        catalog_data = index_data_for(obj)
        self.assertEqual(value, catalog_data.get(idx))

    def assert_solr_data(self, obj, idx, value):
        solr_data = solr_data_for(obj)
        self.assertEqual(value, solr_data.get(idx))

    def assert_solr_and_catalog_data(self, obj, idx, value):
        self.assert_solr_data(obj, idx, value)
        self.assert_catalog_data(obj, idx, value)

    def test_nightly_indexer_indexes_only_passed_indexes(self):
        self.login(self.manager)
        old_creator = self.dossier.Creator()
        new_creator = "New creator"
        self.dossier.creators = (new_creator,)

        self.assert_solr_and_catalog_data(self.dossier, "Creator", old_creator)

        with NightlyIndexer(idxs=["Title"]) as indexer:
            indexer.add_by_obj(self.dossier)

        self.run_nightly_jobs()
        self.assert_solr_and_catalog_data(self.dossier, "Creator", old_creator)

        with NightlyIndexer(idxs=["Title", "Creator"]) as indexer:
            indexer.add_by_obj(self.dossier)

        self.run_nightly_jobs()
        self.assert_solr_and_catalog_data(self.dossier, "Creator", new_creator)

    def test_nightly_solr_only_indexer(self):
        self.login(self.manager)
        old_creator = self.dossier.Creator()
        new_creator = "New creator"
        self.dossier.creators = (new_creator,)

        with NightlyIndexer(idxs=["Title"], index_in_solr_only=True) as indexer:
            indexer.add_by_obj(self.dossier)

        self.run_nightly_jobs()
        self.assert_solr_and_catalog_data(self.dossier, "Creator", old_creator)

        with NightlyIndexer(idxs=["Title", "Creator"], index_in_solr_only=True) as indexer:
            indexer.add_by_obj(self.dossier)

        self.run_nightly_jobs()
        self.assert_solr_data(self.dossier, "Creator", new_creator)
        self.assert_catalog_data(self.dossier, "Creator", old_creator)

    def test_nightly_indexer_handles_multiple_jobs(self):
        self.login(self.manager)
        self.dossier.title = "New dossier title"
        self.empty_dossier.title = "New empty dossier title"
        self.subdossier.title = "New subdossier title"

        with NightlyIndexer(idxs=["Title"]) as indexer:
            indexer.add_by_obj(self.dossier)
            indexer.add_by_obj(self.subdossier)

        with NightlyIndexer(idxs=["Title"]) as indexer:
            indexer.add_by_obj(self.empty_dossier)

        self.run_nightly_jobs()
        self.assert_solr_data(self.dossier, "Title", "New dossier title")
        self.assert_solr_data(self.subdossier, "Title", "New subdossier title")
        self.assert_solr_data(self.empty_dossier, "Title", "New empty dossier title")
        self.assert_catalog_data(
            self.dossier, "Title", ["new", "dossier", "title"])
        self.assert_catalog_data(
            self.subdossier, "Title", ["new", "subdossier", "title"])
        self.assert_catalog_data(
            self.empty_dossier, "Title", ["new", "empty", "dossier", "title"])

    def test_trying_to_reindex_searchable_text_in_solr_raises(self):
        with self.assertRaises(ValueError) as exc:
            NightlyIndexer(idxs=["Title", "SearchableText"],
                           index_in_solr_only=True)
        self.assertEqual(
            'Reindexing SearchableText in solr only is not supported',
            exc.exception.message)


class TestDefaultValuePersister(IntegrationTestCase):

    def run_nightly_jobs(self):
        runner = NightlyJobRunner(force_execution=True)
        runner.execute_pending_jobs()

    def test_persists_only_passed_fields(self):
        intids = getUtility(IIntIds)
        classification = IClassification.get('classification')
        privacy_layer = IClassification.get('privacy_layer')
        public_trial = IClassification.get('public_trial')

        self.login(self.regular_user)

        # Make sure there is no persisted value
        self.dossier.__dict__.pop('classification')
        self.dossier.__dict__.pop('privacy_layer')
        self.dossier.__dict__.pop('public_trial')
        self.assertFalse(object_has_value_for_field(self.dossier, classification))
        self.assertFalse(object_has_value_for_field(self.dossier, privacy_layer))
        self.assertFalse(object_has_value_for_field(self.dossier, public_trial))

        classification_default = IClassification(self.dossier).classification

        with DefaultValuePersister(fields=[classification, public_trial]) as persister:
            persister.add_by_intid(intids.getId(self.dossier))

        self.run_nightly_jobs()

        self.assertTrue(object_has_value_for_field(self.dossier, classification))
        self.assertFalse(object_has_value_for_field(self.dossier, privacy_layer))
        self.assertTrue(object_has_value_for_field(self.dossier, public_trial))
        self.assertEqual(
            public_trial_default(),
            get_persisted_value_for_field(self.dossier, public_trial))
        self.assertEqual(
            classification_default,
            get_persisted_value_for_field(self.dossier, classification))

    def test_does_not_overwrite_already_persisted_values(self):
        intids = getUtility(IIntIds)
        public_trial = IClassification.get("public_trial")

        self.login(self.regular_user)
        self.assertEqual(
            'private',
            get_persisted_value_for_field(self.empty_dossier, public_trial))
        self.assertEqual('unchecked', public_trial_default())

        with DefaultValuePersister(fields=[public_trial]) as persister:
            persister.add_by_intid(intids.getId(self.dossier))

        self.run_nightly_jobs()
        self.assertEqual(
            'private',
            get_persisted_value_for_field(self.empty_dossier, public_trial))

    def test_persist_fields_handles_inexistant_interface(self):
        intids = getUtility(IIntIds)
        self.login(self.regular_user)

        DefaultValuePersister.persist_fields(
            intids.getId(self.dossier),
            fields_tuples=(('inexistent.interface', 'classification'),))

    def test_persist_fields_handles_inexistant_field(self):
        intids = getUtility(IIntIds)
        self.login(self.regular_user)

        DefaultValuePersister.persist_fields(
            intids.getId(self.dossier),
            fields_tuples=((IClassification.__identifier__, 'fieldname'),))

    def test_persist_fields(self):
        intids = getUtility(IIntIds)
        classification = IClassification.get('classification')
        self.login(self.regular_user)

        self.dossier.__dict__.pop('classification')
        self.assertFalse(object_has_value_for_field(self.dossier, classification))

        DefaultValuePersister.persist_fields(
            intids.getId(self.dossier),
            fields_tuples=((IClassification.__identifier__, 'classification'),))

        self.assertTrue(object_has_value_for_field(self.dossier, classification))


class TestNightlyWorkflowSecurityUpdater(IntegrationTestCase):

    def roles_of_permission(self, obj, permission):
        return [role['name'] for role in obj.rolesOfPermission(permission)
                if role['selected'] == 'SELECTED']

    def test_update_workflow_security(self):
        self.login(self.manager)

        with NightlyWorkflowSecurityUpdater(reindex_security=False) as updater:
            updater.update(['opengever_mail_workflow', 'opengever_repositoryroot_workflow'])

        objs = [self.mail_eml, self.mail_msg, self.workspace_mail, self.repository_root]
        expedted_intids = set(map(lambda obj: getUtility(IIntIds).getId(obj), objs))

        runner = NightlyJobRunner(force_execution=True)
        intids = {job.variable_argument for job in
                  runner.job_providers['maintenance-jobs'].queues_manager.jobs}
        self.assertEqual(expedted_intids, intids)

        self.mail_eml.manage_permission('View', roles=['Manager'], acquire=False)
        self.assertEqual(['Manager'], self.roles_of_permission(self.mail_eml, 'View'))

        runner.execute_pending_jobs()
        self.assertEqual(['Administrator', 'CommitteeAdministrator', 'CommitteeMember',
                          'CommitteeResponsible', 'Editor', 'LimitedAdmin', 'Manager',
                          'Reader', 'WorkspaceAdmin', 'WorkspaceGuest', 'WorkspaceMember'],
                         self.roles_of_permission(self.mail_eml, 'View'))
