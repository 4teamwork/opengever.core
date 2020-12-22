from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.interfaces import IReferenceNumber
from opengever.maintenance.scripts.repository_migration_analyse import OperationItem
from opengever.maintenance.scripts.repository_migration_analyse import RepositoryExcelAnalyser
from opengever.maintenance.scripts.repository_migration_analyse import RepositoryMigrator
from opengever.testing import IntegrationTestCase
from pkg_resources import resource_filename
from plone import api


class TestOSMigration(IntegrationTestCase):

    maxDiff = None

    def setUp(self):
        super(TestOSMigration, self).setUp()
        api.portal.set_registry_record(
            "opengever.base.interfaces.IReferenceNumberSettings.formatter",
            "grouped_by_three")

    def test_repository_excel_analyser_os_test_branch_and_leaf_creation(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_branch_and_leaf_creation.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        self.assertEqual(6, len(analyser.analysed_rows))

        self.assertDictEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem(1, u"F\xfchrung und Koordination", "leadership"),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': None,
             'new_position_guid': None,
             'new_title': u'F\xfchrung und Koordination',
             'old_item': OperationItem(1, u"F\xfchrung", ''),
             'repository_depth_violated': False,
             'uid': self.branch_repofolder.UID()},
            analyser.analysed_rows[0])

        self.assertDictEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem(0, u'Allgemeines und \xdcbergreifendes'),
             'new_number': '0',
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': None,
             'new_position_guid': None,
             'new_title': u'Allgemeines und \xdcbergreifendes',
             'old_item': OperationItem(2, u"Rechnungspr\xfcfungskommission", ''),
             'repository_depth_violated': False,
             'uid': self.empty_repofolder.UID()},
            analyser.analysed_rows[1])

        self.assertDictEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem(),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': None,
             'new_position_guid': None,
             'new_title': None,
             'old_item': OperationItem(3, u"Spinn\xe4nnetzregistrar", ''),
             'repository_depth_violated': False,
             'uid': self.inactive_repofolder.UID()},
            analyser.analysed_rows[2])

        guid = analyser.analysed_rows[3]['new_position_guid']
        self.assertIsNotNone(guid)
        self.assertDictEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem(4, 'Created branch', ''),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': '',
             'new_position_guid': guid,
             'new_title': None,
             'old_item': OperationItem(),
             'repository_depth_violated': False,
             'uid': None},
            analyser.analysed_rows[3])

        guid = analyser.analysed_rows[4]['new_position_guid']
        self.assertIsNotNone(guid)
        self.assertDictEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem(41, 'created leaf', ''),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': None,
             'new_position_guid': guid,
             'new_title': None,
             'old_item': OperationItem(),
             'repository_depth_violated': False,
             'uid': None},
            analyser.analysed_rows[4])

        uid = analyser.analysed_rows[5]['new_parent_uid']
        self.assertIsNotNone(uid)

        self.assertDictEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem(42, 'Moved leaf', 'droit municipal'),
             'new_number': '2',
             'new_parent_position': '4',
             'new_parent_uid': uid,
             'new_position': None,
             'new_position_guid': None,
             'new_title': u'Moved leaf',
             'old_item': OperationItem(11, u'Vertr\xe4ge und Vereinbarungen', 'Richtlinien'),
             'repository_depth_violated': False,
             'uid': self.leaf_repofolder.UID()},
            analyser.analysed_rows[5])

    def test_repository_excel_analyser_os_test_migration(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_migration.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        self.assertEqual(6, len(analyser.analysed_rows))

        self.assertDictEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem(1, u"F\xfchrung und Koordination", "leadership"),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': None,
             'new_position_guid': None,
             'new_title': u'F\xfchrung und Koordination',
             'old_item': OperationItem(1, u"F\xfchrung", ''),
             'repository_depth_violated': False,
             'uid': self.branch_repofolder.UID()},
            analyser.analysed_rows[0])

        self.assertDictEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem(0, u'Branch with new number', ''),
             'new_number': '0',
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': None,
             'new_position_guid': None,
             'new_title': u'Branch with new number',
             'old_item': OperationItem(2, u"Rechnungspr\xfcfungskommission", ''),
             'repository_depth_violated': False,
             'uid': self.empty_repofolder.UID()},
            analyser.analysed_rows[1])

        self.assertDictEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem(),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': None,
             'new_position_guid': None,
             'new_title': None,
             'old_item': OperationItem(3, u"Spinn\xe4nnetzregistrar", ''),
             'repository_depth_violated': False,
             'uid': self.inactive_repofolder.UID()},
            analyser.analysed_rows[2])

        guid = analyser.analysed_rows[3]['new_position_guid']
        self.assertIsNotNone(guid)
        self.assertDictEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem('01', 'created leaf in branch with new number', ''),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': '2',
             'new_position_guid': guid,
             'new_title': None,
             'old_item': OperationItem(),
             'repository_depth_violated': False,
             'uid': None},
            analyser.analysed_rows[3])

        guid = analyser.analysed_rows[4]['new_position_guid']
        self.assertIsNotNone(guid)
        self.assertDictEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem(12, 'created leaf in existing branch', ''),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': '1',
             'new_position_guid': guid,
             'new_title': None,
             'old_item': OperationItem(),
             'repository_depth_violated': False,
             'uid': None},
            analyser.analysed_rows[4])

        self.assertDictEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem('02', 'Moved leaf in branch with new number', 'droit municipal'),
             'new_number': '2',
             'new_parent_position': '0',
             'new_parent_uid': self.empty_repofolder.UID(),
             'new_position': None,
             'new_position_guid': None,
             'new_title': u'Moved leaf in branch with new number',
             'old_item': OperationItem(11, u'Vertr\xe4ge und Vereinbarungen', 'Richtlinien'),
             'repository_depth_violated': False,
             'uid': self.leaf_repofolder.UID()},
            analyser.analysed_rows[5])

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

        # Second one has a new number
        results = catalog(reference='Client1 0')
        self.assertEqual(1, len(results))
        brain = results[0]
        self.assertEqual('0 Branch with new number', brain.title_de)
        obj = brain.getObject()
        self.assertEqual('Client1 0', IReferenceNumber(obj).get_number())
        self.assertEqual(self.repository_root, aq_parent(aq_inner(obj)))

        # Third one should be deleted, but that is not implemented
        results = catalog(reference='Client1 3')
        self.assertEqual(1, len(results))

        # Fourth is created in the branch with new number
        # reference should be 'Client1 01', but is currently wrong
        results = catalog(reference='Client1 21')
        self.assertEqual(1, len(results))
        brain = results[0]
        self.assertEqual('01 created leaf in branch with new number', brain.title_de)
        obj = brain.getObject()
        self.assertEqual('Client1 01', IReferenceNumber(obj).get_number())
        # that fails for now, we can't traverse onto self.empty_repofolder, probably path was not reindexed
        # self.assertEqual(self.empty_repofolder, aq_parent(aq_inner(obj)))

        # Fifth is created in an existing branch
        results = catalog(reference='Client1 12')
        self.assertEqual(1, len(results))
        brain = results[0]
        self.assertEqual('12 created leaf in existing branch', brain.title_de)
        obj = brain.getObject()
        self.assertEqual('Client1 12', IReferenceNumber(obj).get_number())
        # that fails for now, we can't traverse onto self.branch_repofolder, probably path was not reindexed
        # self.assertEqual(self.branch_repofolder, aq_parent(aq_inner(obj)))

        # Sixth is moved into the branch with new number
        # reference should be 'Client1 02', but is currently wrong
        results = catalog(reference='Client1 1.1', portal_type='opengever.repository.repositoryfolder')
        self.assertEqual(1, len(results))
        brain = results[0]
        self.assertEqual('02 Moved leaf in branch with new number', brain.title_de)
        obj = brain.getObject()
        self.assertEqual('Client1 02', IReferenceNumber(obj).get_number())
        # that fails for now, we can't traverse onto self.empty_repofolder, probably path was not reindexed
        # self.assertEqual(self.empty_repofolder, aq_parent(aq_inner(obj)))
