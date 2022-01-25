from Acquisition import aq_inner
from Acquisition import aq_parent
from copy import deepcopy
from ftw.builder import Builder
from ftw.builder import create
from opengever.base.indexes import sortable_title
from opengever.base.interfaces import IReferenceNumber
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.base.security import elevated_privileges
from opengever.bundle.sections.constructor import BUNDLE_GUID_KEY
from opengever.globalindex.handlers.task import TaskSqlSyncer
from opengever.maintenance.scripts.repository_migration import MigrationPreconditionsError
from opengever.maintenance.scripts.repository_migration import MigrationValidationError
from opengever.maintenance.scripts.repository_migration import RepositoryExcelAnalyser
from opengever.maintenance.scripts.repository_migration import RepositoryMigrator
from opengever.maintenance.scripts.repository_migration import RepositoryPosition
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from pkg_resources import resource_filename
from plone import api
from plone.app.uuid.utils import uuidToObject
from zope.annotation import IAnnotations
import logging


class ListHandler(logging.Handler):

    def __init__(self, log_list):
        super(ListHandler, self).__init__()
        self.log_list = log_list

    def emit(self, record):
        self.log_list.append(record.msg)


logger = logging.getLogger('opengever.maintenance')


class TestOSMigrationAnalysisPreconditions(IntegrationTestCase):

    def test_raises_if_not_grouped_by_three(self):
        self.login(self.manager)
        with self.assertRaises(AssertionError) as exc:
            RepositoryExcelAnalyser('', '')

        self.assertEqual(
            'Migration is only supported with grouped_by_three',
            exc.exception.message)

    def test_raises_if_more_than_one_reporoot(self):
        self.login(self.manager)
        api.portal.set_registry_record(
            "opengever.base.interfaces.IReferenceNumberSettings.formatter",
            "grouped_by_three")
        RepositoryExcelAnalyser('', '')

        create(Builder('repository_root'))
        with self.assertRaises(AssertionError) as exc:
            RepositoryExcelAnalyser('', '')

        self.assertEqual(
            'Migration is only supported with a single repository root',
            exc.exception.message)


class OSMigrationTestMixin(object):

    def assertObjectConsistency(self, obj, parent_refnum=None, parent_path=None):
        err_msg = "{} not consistent".format(obj.absolute_url_path())
        brain = obj2brain(obj)
        catalog_data = self.get_catalog_indexdata(obj)

        # reference number obtained through the adapter is generated
        # dynamically, hence it should always be correct.
        # reference number in the catalog and in the metadata should match it.
        refnum = IReferenceNumber(obj).get_number()
        self.assertEqual(refnum, brain.reference, err_msg)
        self.assertEqual(refnum, catalog_data['reference'], err_msg)
        if parent_refnum:
            self.assertIn(parent_refnum, IReferenceNumber(obj).get_number(), err_msg)

        self.assertEqual(brain.Description, obj.Description(), err_msg)

        self.assertEqual(brain.getPath(), obj.absolute_url_path(), err_msg)
        self.assertEqual(catalog_data['path'], obj.absolute_url_path(), err_msg)
        if parent_path:
            self.assertIn(parent_path, obj.absolute_url_path(), err_msg)

        if obj.portal_type == 'opengever.repository.repositoryfolder':
            self.assertEqual(brain.title_de, obj.get_prefixed_title_de(), err_msg)
            self.assertEqual(brain.title_fr, obj.get_prefixed_title_fr(), err_msg)
            self.assertEqual(catalog_data['sortable_title'], sortable_title(obj)(), err_msg)

        elif obj.portal_type == 'opengever.task.task':
            model = obj.get_sql_object()
            self.assertEqual(obj.get_reference_number(), model.reference_number)
            self.assertEqual(obj.get_physical_path(), model.physical_path)

    @staticmethod
    def get_changed_rows(rows):
        return [row for row in rows if not row['old_repo_pos'] == row['new_repo_pos']]

    empty_permissions = {'add': [],
                         'block_inheritance': False,
                         'close': [],
                         'edit': [],
                         'manage_dossiers': [],
                         'reactivate': [],
                         'read': []}

    branch_repofolder_data = {
        'is_valid': True,
        'leaf_node_violated': False,
        'local_roles_deleted': False,
        'merge_into': None,
        'new_number': None,
        'new_parent_position': None,
        'new_parent_uid': None,
        'new_position_guid': None,
        'new_position_parent_guid': None,
        'new_position_parent_position': None,
        'new_repo_pos': RepositoryPosition(1, u"F\xfchrung", u"Alles zum Thema F\xfchrung."),
        'new_title': None,
        'old_repo_pos': RepositoryPosition(1, u"F\xfchrung", u"Alles zum Thema F\xfchrung."),
        'permissions': empty_permissions,
        'permissions_disregarded': False,
        'repository_depth_violated': False,
        'set_permissions': False,
        'uid': 'createrepositorytree000000000002'}

    leaf_repofolder_data = {
        'is_valid': True,
        'leaf_node_violated': False,
        'local_roles_deleted': False,
        'merge_into': None,
        'new_number': None,
        'new_parent_position': None,
        'new_parent_uid': None,
        'new_position_guid': None,
        'new_position_parent_guid': None,
        'new_position_parent_position': None,
        'new_repo_pos': RepositoryPosition(11,  u'Vertr\xe4ge und Vereinbarungen', None),
        'new_title': None,
        'old_repo_pos': RepositoryPosition(11,  u'Vertr\xe4ge und Vereinbarungen', None),
        'permissions': empty_permissions,
        'permissions_disregarded': False,
        'repository_depth_violated': False,
        'set_permissions': False,
        'uid': 'createrepositorytree000000000003'}

    empty_repofolder_data = {
        'is_valid': True,
        'leaf_node_violated': False,
        'local_roles_deleted': False,
        'merge_into': None,
        'new_number': None,
        'new_parent_position': None,
        'new_parent_uid': None,
        'new_position_guid': None,
        'new_position_parent_guid': None,
        'new_position_parent_position': None,
        'new_repo_pos': RepositoryPosition(2, u"Rechnungspr\xfcfungskommission", None),
        'new_title': None,
        'old_repo_pos': RepositoryPosition(2, u"Rechnungspr\xfcfungskommission", None),
        'permissions': empty_permissions,
        'permissions_disregarded': False,
        'repository_depth_violated': False,
        'set_permissions': False,
        'uid': 'createrepositorytree000000000004'}

    inactive_repofolder_data = {
        'is_valid': True,
        'leaf_node_violated': False,
        'local_roles_deleted': False,
        'merge_into': None,
        'new_number': None,
        'new_parent_position': None,
        'new_parent_uid': None,
        'new_position_guid': None,
        'new_position_parent_guid': None,
        'new_position_parent_position': None,
        'new_repo_pos': RepositoryPosition(3, u"Spinn\xe4nnetzregistrar", None),
        'new_title': None,
        'old_repo_pos': RepositoryPosition(3, u"Spinn\xe4nnetzregistrar", None),
        'permissions': empty_permissions,
        'permissions_disregarded': False,
        'repository_depth_violated': False,
        'set_permissions': False,
        'uid': 'createrepositorytree000000000005'}


class TestOSMigrationAnalysis(IntegrationTestCase, OSMigrationTestMixin):

    maxDiff = None

    def setUp(self):
        super(TestOSMigrationAnalysis, self).setUp()
        api.portal.set_registry_record(
            "opengever.base.interfaces.IReferenceNumberSettings.formatter",
            "grouped_by_three")
        # We need to reindex all objects after the change of reference number
        # formatter...
        with elevated_privileges():
            res = api.portal.get().portal_catalog.unrestrictedSearchResults(
                path=self.branch_repofolder.absolute_url_path())
            for brain in res:
                brain.getObject().reindexObject()

    def test_repository_excel_analyser_os_test_branch_and_leaf_creation(self):
        self.login(self.manager)

        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_branch_and_leaf_creation.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        self.assertEqual(6, len(analyser.analysed_rows))

        self.assertDictEqual(self.branch_repofolder_data, analyser.analysed_rows[0])

        data = deepcopy(self.empty_repofolder_data)
        data['new_number'] = '0'
        data['new_repo_pos'] = RepositoryPosition(0, u'Allgemeines und \xdcbergreifendes', None)
        data['new_title'] = u'Allgemeines und \xdcbergreifendes'
        self.assertDictEqual(data, analyser.analysed_rows[1])

        self.assertDictEqual(self.inactive_repofolder_data, analyser.analysed_rows[2])

        new_branch_guid = analyser.analysed_rows[3]['new_position_guid']
        reporoot_guid = IAnnotations(self.repository_root).get(BUNDLE_GUID_KEY)
        self.assertIsNotNone(new_branch_guid)
        self.assertDictEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'local_roles_deleted': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(4, 'Created branch', 'comment 1'),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_parent_guid': reporoot_guid,
             'new_position_parent_position': '',
             'new_position_guid': new_branch_guid,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(),
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'repository_depth_violated': False,
             'set_permissions': False,
             'uid': None},
            analyser.analysed_rows[3])

        guid = analyser.analysed_rows[4]['new_position_guid']
        self.assertIsNotNone(guid)
        self.assertDictEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'local_roles_deleted': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(41, 'created leaf', 'comment 2'),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_parent_guid': new_branch_guid,
             'new_position_parent_position': None,
             'new_position_guid': guid,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(),
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'repository_depth_violated': False,
             'set_permissions': False,
             'uid': None},
            analyser.analysed_rows[4])

        uid = analyser.analysed_rows[5]['new_parent_uid']
        self.assertIsNotNone(uid)
        data = deepcopy(self.leaf_repofolder_data)
        data['new_number'] = '2'
        data['new_parent_position'] = '4'
        data['new_parent_uid'] = uid
        data['new_repo_pos'] = RepositoryPosition(42, 'Moved leaf', 'comment for moved one')
        data['new_title'] = u'Moved leaf'
        self.assertDictEqual(data, analyser.analysed_rows[5])

    def test_repository_excel_analyser_os_test_migration(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_migration.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        self.assertEqual(6, len(analyser.analysed_rows))

        data = deepcopy(self.branch_repofolder_data)
        data['new_title'] = u'F\xfchrung und Koordination'
        data['new_repo_pos'] = RepositoryPosition(1, u"F\xfchrung und Koordination", u"Alles zum Thema F\xfchrung.")
        self.assertDictEqual(data, analyser.analysed_rows[0])

        data = deepcopy(self.empty_repofolder_data)
        data['new_number'] = u'0'
        data['new_repo_pos'] = RepositoryPosition(0, u'Branch with new number', '')
        data['new_title'] = u'Branch with new number'
        self.assertDictEqual(data, analyser.analysed_rows[1])

        guid = analyser.analysed_rows[3]['new_position_guid']
        self.assertIsNotNone(guid)

        self.assertDictEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition('01', 'created leaf in branch with new number', 'comment 1'),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': '2',
             'new_position_guid': guid,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': None},
            analyser.analysed_rows[3])

        guid = analyser.analysed_rows[4]['new_position_guid']
        self.assertIsNotNone(guid)
        self.assertDictEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(12, 'created leaf in existing branch', 'comment 2'),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': '1',
             'new_position_guid': guid,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': None},
            analyser.analysed_rows[4])

        data = deepcopy(self.leaf_repofolder_data)
        data['new_number'] = u'2'
        data['new_repo_pos'] = RepositoryPosition('02', 'Moved leaf in branch with new number', 'comment for moved one')
        data['new_title'] = u'Moved leaf in branch with new number'
        data['new_parent_position'] = '0'
        data['new_parent_uid'] = self.empty_repofolder.UID()
        self.assertDictEqual(data, analyser.analysed_rows[5])

    def test_repository_excel_analyser_os_test_invalid(self):
        log_list = []
        handler = ListHandler(log_list)
        logger.addHandler(handler)

        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_invalid.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        self.assertEqual(9, len(analyser.analysed_rows))
        invalid_rows = [row for row in analyser.analysed_rows if not row['is_valid']]
        self.assertEqual(5, len(invalid_rows))

        self.assertEqual(
            {'is_valid': False,
             'leaf_node_violated': True,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition('111', u"Rechnungspr\xfcfungskommission", None),
             'new_number': '1',
             'new_parent_position': '11',
             'new_parent_uid': self.leaf_repofolder.UID(),
             'new_position_guid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition('2', u"Rechnungspr\xfcfungskommission", None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': self.empty_repofolder.UID()},
            invalid_rows[0])
        self.assertIn("leaf node principle violated", log_list[6])

        self.assertEqual(
            {'is_valid': False,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition('41', u"Spinn\xe4nnetzregistrar", None),
             'new_number': '1',
             'new_parent_position': '4',
             'new_parent_uid': None,
             'new_position_guid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition('3', u"Spinn\xe4nnetzregistrar", None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': self.inactive_repofolder.UID()},
            invalid_rows[1])
        self.assertIn(
            "move operation must define new_parent_uid.",
            log_list[7])

        guid = invalid_rows[2]['new_position_guid']
        self.assertEqual(
            {'is_valid': False,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition('51', 'New leaf', None),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_guid': guid,
             'new_position_parent_guid': None,
             'new_position_parent_position': '5',
             'new_title': None,
             'old_repo_pos': RepositoryPosition(None, None, None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': None},
            invalid_rows[2])
        self.assertIn(
            "could not find new parent for create operation.",
            log_list[8])

        guid = invalid_rows[3]['new_position_guid']
        self.assertEqual(
            {'is_valid': False,
             'leaf_node_violated': True,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition('112', 'Second new leaf', None),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_guid': guid,
             'new_position_parent_guid': None,
             'new_position_parent_position': '11',
             'new_title': None,
             'old_repo_pos': RepositoryPosition(None, None, None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': None},
            invalid_rows[3])
        self.assertIn("Invalid operation: parent not found.", log_list[9])
        self.assertIn("leaf node principle violated", log_list[10])

        guid = invalid_rows[4]['new_position_guid']
        parent_guid = invalid_rows[4]['new_position_parent_guid']
        self.assertEqual(
            {'is_valid': False,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition('1211', 'fourth level', None),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_guid': guid,
             'new_position_parent_guid': parent_guid,
             'new_position_parent_position': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(None, None, None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': True,
             'uid': None},
            invalid_rows[4])
        self.assertIn("repository depth violated.", log_list[11])

        logger.removeHandler(handler)


class TestOSMigrationsMigratorPreconditions(IntegrationTestCase):

    def setUp(self):
        super(TestOSMigrationsMigratorPreconditions, self).setUp()
        api.portal.set_registry_record(
            "opengever.base.interfaces.IReferenceNumberSettings.formatter",
            "grouped_by_three")

    def test_raises_if_any_operation_is_invalid(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_invalid.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()
        with self.assertRaises(MigrationPreconditionsError):
            RepositoryMigrator(analyser.analysed_rows)


class TestOSMigrationRun(IntegrationTestCase, OSMigrationTestMixin):

    maxDiff = None

    def setUp(self):
        super(TestOSMigrationRun, self).setUp()
        api.portal.set_registry_record(
            "opengever.base.interfaces.IReferenceNumberSettings.formatter",
            "grouped_by_three")
        # We need to reindex all objects after the change of reference number
        # formatter...
        with elevated_privileges():
            res = api.portal.get().portal_catalog.unrestrictedSearchResults(
                path=self.branch_repofolder.absolute_url_path())
            for brain in res:
                brain.getObject().reindexObject()
                if brain.portal_type == 'opengever.task.task':
                    # make sure that reference number in task model is up to date.
                    TaskSqlSyncer(brain.getObject(), None).sync()

    def test_repository_migrator(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_migration.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        migrator = RepositoryMigrator(analyser.analysed_rows)
        migrator.run()

        catalog = api.portal.get_tool('portal_catalog')

        # First one has a new title
        results = catalog(reference='Client1 1')
        self.assertEqual(1, len(results))
        brain = results[0]
        obj = brain.getObject()
        self.assertEqual(u'1 F\xfchrung und Koordination', brain.title_de)
        self.assertEqual('Client1 1', IReferenceNumber(obj).get_number())
        self.assertEqual(self.repository_root, aq_parent(aq_inner(obj)))
        # Access to fixture objects is done over a lookup table containing
        # the object's path, so won't work anymore.
        # We can simply overrite the attribute though.
        self.branch_repofolder = obj

        # Second one has a new number
        results = catalog(reference='Client1 0')
        self.assertEqual(1, len(results))
        brain = results[0]
        self.assertEqual('0 Branch with new number', brain.title_de)
        obj = brain.getObject()
        self.assertEqual('Client1 0', IReferenceNumber(obj).get_number())
        self.assertEqual(self.repository_root, aq_parent(aq_inner(obj)))
        self.empty_repofolder = obj

        # Third one should be deleted, but that is not implemented
        results = catalog(reference='Client1 3')
        self.assertEqual(1, len(results))

        # Fourth is created in the branch with new number
        results = catalog(reference='Client1 01')
        self.assertEqual(1, len(results))
        brain = results[0]
        self.assertEqual('01 created leaf in branch with new number', brain.title_de)
        obj = brain.getObject()
        self.assertEqual('Client1 01', IReferenceNumber(obj).get_number())
        self.assertEqual(self.empty_repofolder, aq_parent(aq_inner(obj)))

        # Fifth is created in an existing branch
        results = catalog(reference='Client1 12')
        self.assertEqual(1, len(results))
        brain = results[0]
        self.assertEqual('12 created leaf in existing branch', brain.title_de)
        obj = brain.getObject()
        self.assertEqual('Client1 12', IReferenceNumber(obj).get_number())
        self.assertEqual(self.branch_repofolder, aq_parent(aq_inner(obj)))

        # Sixth is moved into the branch with new number
        results = catalog(reference='Client1 02', portal_type='opengever.repository.repositoryfolder')
        self.assertEqual(1, len(results))
        brain = results[0]
        self.assertEqual('02 Moved leaf in branch with new number', brain.title_de)
        obj = brain.getObject()
        self.assertEqual('Client1 02', IReferenceNumber(obj).get_number())
        self.assertEqual(self.empty_repofolder, aq_parent(aq_inner(obj)))
        self.leaf_repofolder = obj

    def test_repository_migrator_change_description(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_change_description.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        self.assertEqual(u"Alles zum Thema F\xfchrung.".encode('utf8'),
                         self.branch_repofolder.Description())

        # We only change the title of branch_repofolder
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(1, len(changed_rows))
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(1, u"F\xfchrung", "New description"),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_position_guid': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(1, u"F\xfchrung", u"Alles zum Thema F\xfchrung."),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': self.branch_repofolder.UID()},
            changed_rows[0])

        migrator = RepositoryMigrator(analyser.analysed_rows)
        migrator.run()

        self.assertEqual(u'New description', self.branch_repofolder.Description())
        self.assertObjectConsistency(self.branch_repofolder)

    def test_repository_migrator_change_refnum(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_change_refnum.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        # We only change the refnum of branch_repofolder (and leaf_repofolder)
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(2, len(changed_rows))
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(0, u"F\xfchrung", u"Alles zum Thema F\xfchrung."),
             'new_number': '0',
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_position_guid': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(1, u"F\xfchrung", u"Alles zum Thema F\xfchrung."),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': self.branch_repofolder.UID()},
            changed_rows[0])
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition('01', u'Vertr\xe4ge und Vereinbarungen', None),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_position_guid': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition('11', u'Vertr\xe4ge und Vereinbarungen', None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': self.leaf_repofolder.UID()},
            changed_rows[1])

        migrator = RepositoryMigrator(analyser.analysed_rows)
        migrator.run()

        self.assertEqual('Client1 0', IReferenceNumber(self.branch_repofolder).get_number())
        self.assertEqual('Client1 01', IReferenceNumber(self.leaf_repofolder).get_number())

        # we check that the reference number of branch_repofolder and all
        # contained objects was updated correctly in the catalog.
        contained_brains = self.portal.portal_catalog.unrestrictedSearchResults(
            path=self.branch_repofolder.absolute_url_path())

        for brain in contained_brains:
            obj = brain.getObject()
            self.assertObjectConsistency(obj, parent_refnum='Client1 0')

    def test_repository_migrator_change_title(self):
        self.login(self.manager)

        # We need to make sure that we are working in German, otherwise setting title_de
        # will not update the id. Will that actually work in production?
        self.request['LANGUAGE_TOOL'].LANGUAGE = 'de'

        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_change_title.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        self.assertEqual('/plone/ordnungssystem/fuhrung', self.branch_repofolder.absolute_url_path())
        self.assertEqual(u'F\xfchrung', self.branch_repofolder.title_de)

        # We only change the title of branch_repofolder
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(1, len(changed_rows))
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(1, "New title", u"Alles zum Thema F\xfchrung."),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_position_guid': None,
             'new_title': u'New title',
             'old_repo_pos': RepositoryPosition(1, u"F\xfchrung", u"Alles zum Thema F\xfchrung."),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': self.branch_repofolder.UID()},
            changed_rows[0])

        migrator = RepositoryMigrator(analyser.analysed_rows)
        migrator.run()

        # path in the lookup table is not correct anymore, so accessing
        # self.branch_repofolder does not work anymore.
        self.branch_repofolder = uuidToObject(changed_rows[0]['uid'])
        self.assertEqual('/plone/ordnungssystem/new-title', self.branch_repofolder.absolute_url_path())
        self.assertEqual(u'New title', self.branch_repofolder.title_de)

        # We check that branch_repofolder and all contained objects were updated
        # correctly
        contained_brains = self.portal.portal_catalog.unrestrictedSearchResults(
            path=self.branch_repofolder.absolute_url_path())

        for brain in contained_brains:
            obj = brain.getObject()
            self.assertObjectConsistency(obj, parent_path='/plone/ordnungssystem/new-title')

    def test_repository_migrator_move(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_move.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        self.assertEqual(
            '/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen',
            self.leaf_repofolder.absolute_url_path())
        parent = aq_parent(aq_inner(self.leaf_repofolder))
        self.assertEqual(self.branch_repofolder, parent)

        # We only move the leaf_repofolder
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(1, len(changed_rows))
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(21, u'Vertr\xe4ge und Vereinbarungen', None),
             'new_number': '1',
             'new_parent_position': '2',
             'new_parent_uid': self.empty_repofolder.UID(),
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_position_guid': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(11, u'Vertr\xe4ge und Vereinbarungen', None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': self.leaf_repofolder.UID()},
            changed_rows[0])

        migrator = RepositoryMigrator(analyser.analysed_rows)
        migrator.run()

        # path in the lookup table is not correct anymore, so accessing
        # self.leaf_repofolder does not work anymore.
        self.leaf_repofolder = uuidToObject(changed_rows[0]['uid'])

        # check that the leaf_repofolder was indeed moved
        self.assertEqual(
            '/plone/ordnungssystem/rechnungsprufungskommission/vertrage-und-vereinbarungen',
            self.leaf_repofolder.absolute_url_path())
        parent = aq_parent(aq_inner(self.leaf_repofolder))
        self.assertEqual(self.empty_repofolder, parent)

        # We check that leaf_repofolder and all contained objects were updated
        # correctly
        contained_brains = self.portal.portal_catalog.unrestrictedSearchResults(
            path=self.leaf_repofolder.absolute_url_path())

        for brain in contained_brains:
            obj = brain.getObject()
            self.assertObjectConsistency(obj, parent_path=self.leaf_repofolder.absolute_url_path())

    def test_repository_migrator_create_leaf(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_create.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        results = self.portal.portal_catalog.unrestrictedSearchResults(
            Title="New leaf")
        self.assertEqual(0, len(results))

        # We only create the new repofolder
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(1, len(changed_rows))
        guid = changed_rows[0]['new_position_guid']
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(12, u'New leaf', 'New description'),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': '1',
             'new_position_guid': guid,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(),
             'permissions':  {
                'add': [u'group1'],
                'block_inheritance': True,
                'close': [u'group2', u'group3'],
                'edit': [u'group1'],
                'manage_dossiers': [],
                'reactivate': [],
                'read': [u'group1', u'group2']
                },
             'local_roles_deleted': False,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': None},
            changed_rows[0])

        migrator = RepositoryMigrator(analyser.analysed_rows)
        migrator.run()

        # check that the new repofolder was indeed created
        results = self.portal.portal_catalog.unrestrictedSearchResults(
            Title="New leaf")
        self.assertEqual(1, len(results))
        obj = results[0].getObject()

        self.assertEqual('New leaf', obj.title_de)
        self.assertEqual('Client1 12', IReferenceNumber(obj).get_number())
        self.assertEqual('/plone/ordnungssystem/fuhrung/new-leaf',
                         obj.absolute_url_path())
        parent = aq_parent(aq_inner(obj))
        self.assertEqual(self.branch_repofolder, parent)

        # Now we check for consistency in the catalog
        self.assertObjectConsistency(obj)

    def test_repository_migrator_create_branch_and_leaf_in_reporoot(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_create_in_reporoot.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        # We only create the new repofolder
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(2, len(changed_rows))
        branch_guid = changed_rows[0]['new_position_guid']
        self.assertIsNotNone(branch_guid)
        reporoot_guid = IAnnotations(self.repository_root).get(BUNDLE_GUID_KEY)
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(4, u'New branch', 'New description'),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_parent_guid': reporoot_guid,
             'new_position_parent_position': '',
             'new_position_guid': branch_guid,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': None},
            changed_rows[0])
        guid = changed_rows[1]['new_position_guid']
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(41, u'New leaf', 'New leaf description'),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_parent_guid': branch_guid,
             'new_position_parent_position': None,
             'new_position_guid': guid,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': None},
            changed_rows[1])

        with self.observe_children(self.repository_root) as children:
            migrator = RepositoryMigrator(analyser.analysed_rows)
            migrator.run()

        # check that the new branch repofolder was indeed created
        self.assertEqual(1, len(children['added']))
        branch = children['added'].pop()

        self.assertEqual('New branch', branch.title_de)
        self.assertEqual('Client1 4', IReferenceNumber(branch).get_number())
        self.assertEqual('/plone/ordnungssystem/new-branch',
                         branch.absolute_url_path())
        parent = aq_parent(aq_inner(branch))
        self.assertEqual(self.repository_root, parent)

        # check that the new leaf repofolder was indeed created
        self.assertEqual(1, len(branch.contentItems()))
        leaf = branch.contentItems()[0][1]

        self.assertEqual('New leaf', leaf.title_de)
        self.assertEqual('Client1 41', IReferenceNumber(leaf).get_number())
        self.assertEqual('/plone/ordnungssystem/new-branch/new-leaf',
                         leaf.absolute_url_path())
        parent = aq_parent(aq_inner(leaf))
        self.assertEqual(branch, parent)

        # Now we check for consistency in the catalog
        self.assertObjectConsistency(branch)
        self.assertObjectConsistency(leaf)

    def test_repository_migrator_create_in_moved_repofolder(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_create_in_moved_repofolder.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        self.assertEqual(
            '/plone/ordnungssystem/rechnungsprufungskommission',
            self.empty_repofolder.absolute_url_path())

        # We create a new repofolder and move the leaf_repofolder into it
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(2, len(changed_rows))

        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(12, u"Rechnungspr\xfcfungskommission", None),
             'new_number': '2',
             'new_parent_position': '1',
             'new_parent_uid': self.branch_repofolder.UID(),
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_position_guid': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(2, u"Rechnungspr\xfcfungskommission", None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': self.empty_repofolder.UID()},
            changed_rows[0])

        guid = changed_rows[1]['new_position_guid']
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(121, u'New leaf', 'New description'),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_guid': guid,
             'new_position_parent_guid': None,
             'new_position_parent_position': '2',
             'new_title': None,
             'old_repo_pos': RepositoryPosition(),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': None},
            changed_rows[1])

        with self.observe_children(self.branch_repofolder) as branch_children,\
                self.observe_children(self.repository_root) as root_children:
            migrator = RepositoryMigrator(analyser.analysed_rows)
            migrator.run()

        # check that the empty_repofolder was indeed moved
        self.assertEqual(1, len(branch_children['added']))
        self.assertEqual(branch_children['added'], root_children['removed'])
        moved_repofolder = branch_children['added'].pop()
        self.assertEqual(
            '/plone/ordnungssystem/fuhrung/rechnungsprufungskommission',
            moved_repofolder.absolute_url_path())

        # check that the new repofolder was indeed created
        self.assertEqual(1, len(moved_repofolder.contentItems()))
        new_repofolder = moved_repofolder.contentItems()[0][1]
        self.assertEqual('New leaf', new_repofolder.title_de)
        self.assertEqual('Client1 121', IReferenceNumber(new_repofolder).get_number())
        self.assertEqual(
            '/plone/ordnungssystem/fuhrung/rechnungsprufungskommission/new-leaf',
            new_repofolder.absolute_url_path())

        # We check that the moved repofolder and all contained objects were
        # updated correctly
        contained_brains = self.portal.portal_catalog.unrestrictedSearchResults(
            path=moved_repofolder.absolute_url_path())

        for brain in contained_brains:
            obj = brain.getObject()
            self.assertObjectConsistency(
                obj, parent_refnum='Client1 12',
                parent_path=moved_repofolder.absolute_url_path())

    def test_repository_migrator_move_into_created_repofolder(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_move_into_created_repofolder.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        self.assertEqual(
            '/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen',
            self.leaf_repofolder.absolute_url_path())
        parent = aq_parent(aq_inner(self.leaf_repofolder))
        self.assertEqual(self.branch_repofolder, parent)

        # We create a new repofolder and move the leaf_repofolder into it
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(2, len(changed_rows))

        branch_guid = changed_rows[0]['new_position_guid']
        self.assertIsNotNone(branch_guid)
        reporoot_guid = IAnnotations(self.repository_root).get(BUNDLE_GUID_KEY)
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(4, u'New branch', 'New description'),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_guid': branch_guid,
             'new_position_parent_guid': reporoot_guid,
             'new_position_parent_position': '',
             'new_title': None,
             'old_repo_pos': RepositoryPosition(),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': None},
            changed_rows[0])

        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(41, u'Vertr\xe4ge und Vereinbarungen', None),
             'new_number': '1',
             'new_parent_position': '4',
             'new_parent_uid': branch_guid,
             'new_position_guid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(11, u'Vertr\xe4ge und Vereinbarungen', None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid':  self.leaf_repofolder.UID()},
            changed_rows[1])

        with self.observe_children(self.branch_repofolder) as branch_children,\
                self.observe_children(self.repository_root) as root_children:
            migrator = RepositoryMigrator(analyser.analysed_rows)
            migrator.run()

        # check that the new repository folder was created
        self.assertEqual(1, len(root_children['added']))
        new_branch = root_children['added'].pop()

        # check that leaf_repofolder was moved
        self.assertEqual(1, len(branch_children['removed']))
        self.assertEqual(1, len(new_branch.contentItems()))
        moved_leaf = new_branch.contentItems()[0][1]
        self.assertEqual(branch_children['removed'].pop(), moved_leaf)

        self.assertEqual(
            '/plone/ordnungssystem/new-branch/vertrage-und-vereinbarungen',
            moved_leaf.absolute_url_path())
        parent = aq_parent(aq_inner(moved_leaf))
        self.assertEqual(new_branch, parent)

        # We check that new_branch and all contained objects were updated
        # correctly
        contained_brains = self.portal.portal_catalog.unrestrictedSearchResults(
            path=new_branch.absolute_url_path())

        for brain in contained_brains:
            obj = brain.getObject()
            self.assertObjectConsistency(
                obj, parent_path=new_branch.absolute_url_path(),
                parent_refnum='Client1 4')

    def test_repository_migrator_move_into_repository_root(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_move_into_reporoot.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        self.assertEqual(
            '/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen',
            self.leaf_repofolder.absolute_url_path())
        parent = aq_parent(aq_inner(self.leaf_repofolder))
        self.assertEqual(self.branch_repofolder, parent)

        # We only move the leaf_repofolder
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(1, len(changed_rows))
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(4, u'Vertr\xe4ge und Vereinbarungen', None),
             'new_number': '4',
             'new_parent_position': '',
             'new_parent_uid': self.repository_root.UID(),
             'new_position_guid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(11, u'Vertr\xe4ge und Vereinbarungen', None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': self.leaf_repofolder.UID()},
            changed_rows[0])

        with self.observe_children(self.branch_repofolder) as branch_children,\
                self.observe_children(self.repository_root) as root_children:
            migrator = RepositoryMigrator(analyser.analysed_rows)
            migrator.run()

        self.assertEqual(1, len(branch_children['removed']))
        self.assertEqual(branch_children['removed'], root_children['added'])

        # path in the lookup table is not correct anymore, so accessing
        # self.leaf_repofolder does not work anymore.
        self.leaf_repofolder = root_children['added'].pop()

        # check that the leaf_repofolder was indeed moved
        self.assertEqual(
            '/plone/ordnungssystem/vertrage-und-vereinbarungen',
            self.leaf_repofolder.absolute_url_path())
        parent = aq_parent(aq_inner(self.leaf_repofolder))
        self.assertEqual(self.repository_root, parent)

        # and its reference number updated
        self.assertEqual(
            'Client1 4', IReferenceNumber(self.leaf_repofolder).get_number())

        # We check that leaf_repofolder and all contained objects were updated
        # correctly
        contained_brains = self.portal.portal_catalog.unrestrictedSearchResults(
            path=self.leaf_repofolder.absolute_url_path())

        for brain in contained_brains:
            obj = brain.getObject()
            self.assertObjectConsistency(
                obj, parent_path=self.repository_root.absolute_url_path(),
                parent_refnum='Client1 4')

    def test_repository_migrator_move_into_moved_repofolder(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_move_into_moved_repofolder.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        self.assertEqual(
            '/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen',
            self.leaf_repofolder.absolute_url_path())
        parent = aq_parent(aq_inner(self.leaf_repofolder))
        self.assertEqual(self.branch_repofolder, parent)

        self.assertEqual(
            '/plone/ordnungssystem/rechnungsprufungskommission',
            self.empty_repofolder.absolute_url_path())
        parent = aq_parent(aq_inner(self.empty_repofolder))
        self.assertEqual(self.repository_root, parent)

        # We move the leaf_repofolder into the reporoot and then the
        # incative_repofolder into it
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(2, len(changed_rows))
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(12, u"Rechnungspr\xfcfungskommission", None),
             'new_number': '2',
             'new_parent_position': '1',
             'new_parent_uid': self.branch_repofolder.UID(),
             'new_position_guid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(2, u"Rechnungspr\xfcfungskommission", ''),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': self.empty_repofolder.UID()},
            changed_rows[0])
        self.assertDictEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(121, u'Vertr\xe4ge und Vereinbarungen', ''),
             'new_number': '1',
             'new_parent_position': '12',
             'new_parent_uid': self.empty_repofolder.UID(),
             'new_position_guid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(11, u'Vertr\xe4ge und Vereinbarungen', None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': self.leaf_repofolder.UID()},
            changed_rows[1])

        with self.observe_children(self.branch_repofolder) as branch_children,\
                self.observe_children(self.repository_root) as root_children:
            migrator = RepositoryMigrator(analyser.analysed_rows)
            migrator.run()

        # Check that the empty_repofolder was moved
        self.assertEqual(1, len(branch_children['added']))
        self.assertEqual(branch_children['added'], root_children['removed'])
        self.empty_repofolder = branch_children['added'].pop()

        self.assertEqual(
            '/plone/ordnungssystem/fuhrung/rechnungsprufungskommission',
            self.empty_repofolder.absolute_url_path())
        parent = aq_parent(aq_inner(self.empty_repofolder))
        self.assertEqual(self.branch_repofolder, parent)

        # and its reference number updated
        self.assertEqual(
            'Client1 12', IReferenceNumber(self.empty_repofolder).get_number())

        # Check that the leaf_repofolder was moved
        self.assertEqual(1, len(branch_children['removed']))
        self.assertEqual(1, len(self.empty_repofolder.contentItems()))
        self.leaf_repofolder = self.empty_repofolder.contentItems()[0][1]
        self.assertEqual(branch_children['removed'].pop(), self.leaf_repofolder)

        self.assertEqual(
            '/plone/ordnungssystem/fuhrung/rechnungsprufungskommission/vertrage-und-vereinbarungen',
            self.leaf_repofolder.absolute_url_path())
        parent = aq_parent(aq_inner(self.leaf_repofolder))
        self.assertEqual(self.empty_repofolder, parent)

        # and its reference number updated
        self.assertEqual(
            'Client1 121', IReferenceNumber(self.leaf_repofolder).get_number())

        # We check that leaf_repofolder and all contained objects were updated
        # correctly
        contained_brains = self.portal.portal_catalog.unrestrictedSearchResults(
            path=self.empty_repofolder.absolute_url_path())

        for brain in contained_brains:
            obj = brain.getObject()
            self.assertObjectConsistency(
                obj, parent_path=self.empty_repofolder.absolute_url_path(),
                parent_refnum='Client1 12')

    def test_repository_migrator_move_and_change_child_refnum(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_move_and_change_child_refnum.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        migrator = RepositoryMigrator(analyser.analysed_rows)
        # This will validate that the reference numbers were set correctly
        migrator.run()

    def get_allowed_users(self, obj):
        return filter(lambda x: x.startswith("user:"),
                      self.get_catalog_indexdata(obj)['allowedRolesAndUsers'])

    def test_repository_migrator_move_updates_permissions_correctly(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_move.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()
        changed_rows = self.get_changed_rows(analyser.analysed_rows)

        self.assertItemsEqual(['user:fa_users', 'user:jurgen.fischer'],
                              self.get_allowed_users(self.leaf_repofolder))
        self.assertItemsEqual(['user:fa_users', 'user:jurgen.fischer'],
                              self.get_allowed_users(self.branch_repofolder))
        self.assertItemsEqual(['user:fa_users', 'user:jurgen.fischer'],
                              self.get_allowed_users(self.empty_repofolder))
        self.assertItemsEqual(
            ['user:fa_inbox_users', 'user:fa_users', 'user:jurgen.fischer', 'user:kathi.barfuss'],
            self.get_allowed_users(self.dossier))

        RoleAssignmentManager(self.branch_repofolder).add_or_update_assignment(
            SharingRoleAssignment(self.reader_user.getId(), ['Reader']))

        RoleAssignmentManager(self.empty_repofolder).add_or_update_assignment(
            SharingRoleAssignment(self.workspace_guest.getId(), ['Reader']))

        self.assertItemsEqual([
            'user:lucklicher.laser', 'user:fa_users', 'user:jurgen.fischer'],
            self.get_allowed_users(self.branch_repofolder))
        self.assertItemsEqual([
            'user:hans.peter', 'user:fa_users', 'user:jurgen.fischer'],
            self.get_allowed_users(self.empty_repofolder))
        # because of inheritance, lucklicher.laser now has reader permissions
        # on both leaf_repofolder and dossier
        self.assertItemsEqual([
            'user:lucklicher.laser', 'user:fa_users', 'user:jurgen.fischer'],
            self.get_allowed_users(self.leaf_repofolder))
        self.assertItemsEqual(
            ['user:lucklicher.laser', 'user:fa_inbox_users', 'user:fa_users', 'user:jurgen.fischer', 'user:kathi.barfuss'],
            self.get_allowed_users(self.dossier))

        # We move leaf_repofolder from branch_repofolder to empty_repofolder
        dossier_uid = self.dossier.UID()
        migrator = RepositoryMigrator(analyser.analysed_rows)
        migrator.run()

        # path in the lookup table is not correct anymore, so accessing
        # self.leaf_repofolder does not work anymore.
        self.leaf_repofolder = uuidToObject(changed_rows[0]['uid'])
        self.dossier = uuidToObject(dossier_uid)

        # lucklicher.laser has lost his permissions as it was inherited from
        # branch_repofolder, while hans.peter now has reader permissions on
        # both leaf_repofolder and dossier as it is inherited from the new parent
        self.assertItemsEqual([
            'user:hans.peter', 'user:fa_users', 'user:jurgen.fischer'],
            self.get_allowed_users(self.leaf_repofolder))
        self.assertItemsEqual(
            ['user:hans.peter', 'user:fa_inbox_users', 'user:fa_users', 'user:jurgen.fischer', 'user:kathi.barfuss'],
            self.get_allowed_users(self.dossier))

    def test_repository_migrator_move_updates_blocked_permissions_correctly(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_move.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()
        changed_rows = self.get_changed_rows(analyser.analysed_rows)

        RoleAssignmentManager(self.branch_repofolder).add_or_update_assignment(
            SharingRoleAssignment(self.reader_user.getId(), ['Reader']))

        RoleAssignmentManager(self.empty_repofolder).add_or_update_assignment(
            SharingRoleAssignment(self.workspace_guest.getId(), ['Reader']))

        self.assertItemsEqual(['user:lucklicher.laser', 'user:fa_users', 'user:jurgen.fischer'],
                              self.get_allowed_users(self.leaf_repofolder))
        self.assertItemsEqual(
            ['user:lucklicher.laser', 'user:fa_inbox_users', 'user:fa_users', 'user:jurgen.fischer', 'user:kathi.barfuss'],
            self.get_allowed_users(self.dossier))

        self.leaf_repofolder.__ac_local_roles_block__ = True
        self.leaf_repofolder.reindexObjectSecurity()

        self.assertItemsEqual([], self.get_allowed_users(self.leaf_repofolder))
        self.assertItemsEqual(
            ['user:fa_inbox_users', 'user:kathi.barfuss'],
            self.get_allowed_users(self.dossier))

        # We move leaf_repofolder from branch_repofolder to empty_repofolder
        dossier_uid = self.dossier.UID()
        migrator = RepositoryMigrator(analyser.analysed_rows)
        migrator.run()

        # path in the lookup table is not correct anymore, so accessing
        # self.leaf_repofolder does not work anymore.
        self.leaf_repofolder = uuidToObject(changed_rows[0]['uid'])
        self.dossier = uuidToObject(dossier_uid)

        # Note that reader permission of hans.peter was not inherited from
        # empty_repofolder
        self.assertItemsEqual([], self.get_allowed_users(self.leaf_repofolder))
        self.assertItemsEqual(
            ['user:fa_inbox_users', 'user:kathi.barfuss'],
            self.get_allowed_users(self.dossier))

    def test_repository_migrator_sets_permissions_correctly(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_create.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        # We only create the new repofolder
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(1, len(changed_rows))
        guid = changed_rows[0]['new_position_guid']
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(12, u'New leaf', 'New description'),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': '1',
             'new_position_guid': guid,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(),
             'local_roles_deleted': False,
             'permissions_disregarded': False,
             'set_permissions': False,
             'permissions':  {
                'add': [u'group1'],
                'block_inheritance': True,
                'close': [u'group2', u'group3'],
                'edit': [u'group1'],
                'manage_dossiers': [],
                'reactivate': [],
                'read': [u'group1', u'group2']
                },
             'repository_depth_violated': False,
             'uid': None},
            changed_rows[0])

        self.assertEqual(
            False, getattr(self.branch_repofolder, '__ac_local_roles_block__', False))
        self.assertDictEqual(
            {'faivel.fruhling': ['DossierManager'],
             'nicole.kohler': ['Owner']},
            self.branch_repofolder.__ac_local_roles__)

        with self.observe_children(self.branch_repofolder) as children:
            migrator = RepositoryMigrator(analyser.analysed_rows)
            migrator.run()

        self.assertEqual(1, len(children['added']))
        created = children['added'].pop()
        self.assertEqual(True, getattr(created, '__ac_local_roles_block__', False))
        self.assertDictEqual(
            {'admin': ['Owner'],
             'group1': ['Contributor', 'Editor', 'Reader'],
             'group2': ['Reviewer', 'Reader'],
             'group3': ['Reviewer']},
            created.__ac_local_roles__)

        # Check that permissions were not changed on branch_repofolder
        self.assertEqual(
            True, getattr(self.branch_repofolder, '__ac_local_roles_block__', True))

        self.assertDictEqual(
            {u'group1': ['Contributor', 'Reader'],
             u'group2': ['Reader'],
             'nicole.kohler': ['Owner']},
            self.branch_repofolder.__ac_local_roles__)

    def test_repository_migrator_merge_into_existing_repofolder(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_merge_into_existing_repofolder.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        # We merge leaf_repofolder into empty_repofolder
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(1, len(changed_rows))

        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': self.empty_repofolder.UID(),
             'new_repo_pos': RepositoryPosition(2, u'Vertr\xe4ge und Vereinbarungen', None),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_guid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(11, u'Vertr\xe4ge und Vereinbarungen', None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': self.leaf_repofolder.UID()},
            changed_rows[0])

        migrator = RepositoryMigrator(analyser.analysed_rows)
        self.assertEqual(1, len(migrator.items_to_merge()))
        self.assertEqual(changed_rows, migrator.items_to_merge())

        directly_contained = self.leaf_repofolder.contentValues()
        contained = self.portal.portal_catalog.unrestrictedSearchResults(
                path={'query': self.leaf_repofolder.absolute_url_path(),
                      'exclude_root': True})
        contained_uids = [brain.UID for brain in contained]
        self.assertEqual(16, len(directly_contained))
        self.assertEqual(59, len(contained_uids))

        with self.observe_children(self.branch_repofolder) as branch_children,\
                self.observe_children(self.empty_repofolder) as children:
            migrator.run()

        # check that branch_repofolder was deleted
        self.assertEqual(1, len(branch_children['removed']))

        # check that the content of the leaf_folder was moved
        self.assertEqual(16, len(children['added']))
        self.assertItemsEqual(directly_contained, children['added'])

        # We check that new_branch and all contained objects were updated
        # correctly
        contained_brains = self.portal.portal_catalog.unrestrictedSearchResults(
            path={'query': self.empty_repofolder.absolute_url_path(),
                  'exclude_root': True})

        self.assertItemsEqual([brain.UID for brain in contained_brains],
                              contained_uids)

        for brain in contained_brains:
            obj = brain.getObject()
            self.assertObjectConsistency(
                obj, parent_path=self.empty_repofolder.absolute_url_path(),
                parent_refnum='Client1 2')

    def test_repository_migrator_merge_into_created_repofolder(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_merge_into_created_repofolder.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        # We create a new repofolder and merge leaf_repofolder into it
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(2, len(changed_rows))

        guid = changed_rows[0]['new_position_guid']
        reporoot_guid = IAnnotations(self.repository_root).get(BUNDLE_GUID_KEY)
        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': None,
             'new_repo_pos': RepositoryPosition(4, u'Vertr\xe4ge und Vereinbarungen', None),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_guid': guid,
             'new_position_parent_guid': reporoot_guid,
             'new_position_parent_position': '',
             'new_title': None,
             'old_repo_pos': RepositoryPosition(None, None, None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': None},
            changed_rows[0])

        self.assertEqual(
            {'is_valid': True,
             'leaf_node_violated': False,
             'merge_into': guid,
             'new_repo_pos': RepositoryPosition(4, u'Vertr\xe4ge und Vereinbarungen', None),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position_guid': None,
             'new_position_parent_guid': None,
             'new_position_parent_position': None,
             'new_title': None,
             'old_repo_pos': RepositoryPosition(11, u'Vertr\xe4ge und Vereinbarungen', None),
             'local_roles_deleted': False,
             'permissions': self.empty_permissions,
             'permissions_disregarded': False,
             'set_permissions': False,
             'repository_depth_violated': False,
             'uid': self.leaf_repofolder.UID()},
            changed_rows[1])

        migrator = RepositoryMigrator(analyser.analysed_rows)
        self.assertEqual(1, len(migrator.items_to_merge()))

        directly_contained = self.leaf_repofolder.contentValues()
        contained = self.portal.portal_catalog.unrestrictedSearchResults(
                path={'query': self.leaf_repofolder.absolute_url_path(),
                      'exclude_root': True})
        contained_uids = [brain.UID for brain in contained]
        self.assertEqual(16, len(directly_contained))
        self.assertEqual(59, len(contained_uids))

        with self.observe_children(self.branch_repofolder) as branch_children,\
                self.observe_children(self.repository_root) as children:
            migrator.run()

        # check that branch_repofolder was deleted
        self.assertEqual(1, len(branch_children['removed']))

        # check that the content of the leaf_folder was moved
        self.assertEqual(1, len(children['added']))
        new_repofolder = children['added'].pop()

        self.assertItemsEqual(directly_contained, new_repofolder.contentValues())

        # We check that new_branch and all contained objects were updated
        # correctly
        contained_brains = self.portal.portal_catalog.unrestrictedSearchResults(
            path={'query': new_repofolder.absolute_url_path()})

        contained_uids.append(new_repofolder.UID())
        self.assertItemsEqual([brain.UID for brain in contained_brains],
                              contained_uids)

        for brain in contained_brains:
            obj = brain.getObject()
            self.assertObjectConsistency(
                obj, parent_path=self.repository_root.absolute_url_path(),
                parent_refnum='Client1 4')


class TestOSMigrationValidation(IntegrationTestCase, OSMigrationTestMixin):

    maxDiff = None

    def setUp(self):
        super(TestOSMigrationValidation, self).setUp()
        api.portal.set_registry_record(
            "opengever.base.interfaces.IReferenceNumberSettings.formatter",
            "grouped_by_three")
        # We need to reindex all objects after the change of reference number
        # formatter...
        with elevated_privileges():
            res = api.portal.get().portal_catalog.unrestrictedSearchResults(
                path=self.branch_repofolder.absolute_url_path())
            for brain in res:
                brain.getObject().reindexObject()

    def test_validation_fails_if_title_is_not_set_correctly(self):
        self.login(self.manager)

        # We need to make sure that we are working in German, otherwise setting title_de
        # will not update the id. Will that actually work in production?
        self.request['LANGUAGE_TOOL'].LANGUAGE = 'de'

        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_no_changes.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        # we do nothing here
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(0, len(changed_rows))

        migrator = RepositoryMigrator(analyser.analysed_rows)
        migrator.run()
        migrator.validate()

        self.branch_repofolder.title_de = "modified"
        with self.assertRaises(MigrationValidationError):
            migrator.validate()

        self.assertEqual([self.branch_repofolder.UID()],
                         migrator.validation_errors.keys())
        self.assertEqual(
            [(u'F\xfchrung', 'modified', 'incorrect title'),
             (u'1 F\xfchrung', u'1 modified', 'data inconsistency'),
             ('0001 fuhrung', '0001 modified', 'data inconsistency')],
            migrator.validation_errors[self.branch_repofolder.UID()])

    def test_validation_fails_if_uid_cannot_be_resolved(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_no_changes.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        # we do nothing here
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(0, len(changed_rows))

        migrator = RepositoryMigrator(analyser.analysed_rows)
        migrator.run()
        migrator.validate()

        migrator.operations_list[0]['uid'] = "foo"
        with self.assertRaises(MigrationValidationError):
            migrator.validate()

        self.assertEqual(0, len(migrator.validation_errors))
        self.assertTrue(migrator.validation_failed)

    def test_validation_does_not_fail_if_data_is_not_consistent(self):
        self.login(self.manager)

        # We need to make sure that we are working in German, otherwise setting title_de
        # will not update the id. Will that actually work in production?
        self.request['LANGUAGE_TOOL'].LANGUAGE = 'de'

        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_no_changes.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        # we do nothing here
        changed_rows = self.get_changed_rows(analyser.analysed_rows)
        self.assertEqual(0, len(changed_rows))

        migrator = RepositoryMigrator(analyser.analysed_rows)
        migrator.run()
        migrator.validate()

        initial_title = self.branch_repofolder.title_de
        self.branch_repofolder.title_de = "modified"
        self.branch_repofolder.reindexObject()
        self.branch_repofolder.title_de = initial_title
        # data consistency in catalog is not enough to make the migration fail
        # but it adds validation errors
        migrator.validate()

        self.assertEqual([self.branch_repofolder.UID()],
                         migrator.validation_errors.keys())
        self.assertEqual(
            [(u'1 modified', u'1 F\xfchrung', 'data inconsistency'),
             ('0001 modified', '0001 fuhrung', 'data inconsistency')],
            migrator.validation_errors[self.branch_repofolder.UID()])
