from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.indexes import sortable_title
from opengever.base.interfaces import IReferenceNumber
from opengever.base.security import elevated_privileges
from opengever.maintenance.scripts.repository_migration_analyse import OperationItem
from opengever.maintenance.scripts.repository_migration_analyse import RepositoryExcelAnalyser
from opengever.maintenance.scripts.repository_migration_analyse import RepositoryMigrator
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from pkg_resources import resource_filename
from plone import api
from plone.app.uuid.utils import uuidToObject


class TestOSMigration(IntegrationTestCase):

    maxDiff = None

    def setUp(self):
        super(TestOSMigration, self).setUp()
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

        if not obj.portal_type == 'opengever.repository.repositoryfolder':
            return
        self.assertEqual(brain.title_de, obj.get_prefixed_title_de(), err_msg)
        self.assertEqual(brain.title_fr, obj.get_prefixed_title_fr(), err_msg)
        self.assertEqual(catalog_data['sortable_title'], sortable_title(obj)(), err_msg)

    @staticmethod
    def get_changed_rows(rows):
        return [row for row in rows if not row['old_item'] == row['new_item']]

    def test_repository_excel_analyser_os_test_branch_and_leaf_creation(self):
        self.login(self.manager)
        migration_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/os_test_branch_and_leaf_creation.xlsx')
        analysis_file = resource_filename('opengever.bundle.tests', 'assets/os_migration/test_analysis.xlsx')
        analyser = RepositoryExcelAnalyser(migration_file, analysis_file)
        analyser.analyse()

        self.assertEqual(6, len(analyser.analysed_rows))

        self.assertDictEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem(1, u"F\xfchrung und Koordination", ""),
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
             'new_item': OperationItem(4, 'Created branch', 'comment 1'),
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
             'new_item': OperationItem(41, 'created leaf', 'comment 2'),
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
             'new_item': OperationItem(42, 'Moved leaf', 'comment for moved one'),
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
             'new_item': OperationItem(1, u"F\xfchrung und Koordination", ""),
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
             'new_item': OperationItem('01', 'created leaf in branch with new number', 'comment 1'),
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
             'new_item': OperationItem(12, 'created leaf in existing branch', 'comment 2'),
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
             'new_item': OperationItem('02', 'Moved leaf in branch with new number', 'comment for moved one'),
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
            {'leaf_node_violated': False,
             'new_item': OperationItem(1, u"F\xfchrung", "New description"),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': None,
             'new_position_guid': None,
             'new_title': None,
             'old_item': OperationItem(1, u"F\xfchrung", u"Alles zum Thema F\xfchrung."),
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
            {'leaf_node_violated': False,
             'new_item': OperationItem(0, u"F\xfchrung", u"Alles zum Thema F\xfchrung."),
             'new_number': '0',
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': None,
             'new_position_guid': None,
             'new_title': None,
             'old_item': OperationItem(1, u"F\xfchrung", u"Alles zum Thema F\xfchrung."),
             'repository_depth_violated': False,
             'uid': self.branch_repofolder.UID()},
            changed_rows[0])
        self.assertEqual(
            {'leaf_node_violated': False,
             'new_item': OperationItem('01', u'Vertr\xe4ge und Vereinbarungen', None),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': None,
             'new_position_guid': None,
             'new_title': None,
             'old_item': OperationItem('11', u'Vertr\xe4ge und Vereinbarungen', None),
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
            {'leaf_node_violated': False,
             'new_item': OperationItem(1, "New title", u"Alles zum Thema F\xfchrung."),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': None,
             'new_position_guid': None,
             'new_title': u'New title',
             'old_item': OperationItem(1, u"F\xfchrung", u"Alles zum Thema F\xfchrung."),
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
            {'leaf_node_violated': False,
             'new_item': OperationItem(21, u'Vertr\xe4ge und Vereinbarungen', None),
             'new_number': '1',
             'new_parent_position': '2',
             'new_parent_uid': self.empty_repofolder.UID(),
             'new_position': None,
             'new_position_guid': None,
             'new_title': None,
             'old_item': OperationItem(11, u'Vertr\xe4ge und Vereinbarungen', None),
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

    def test_repository_migrator_create(self):
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
            {'leaf_node_violated': False,
             'new_item': OperationItem(12, u'New leaf', 'New description'),
             'new_number': None,
             'new_parent_position': None,
             'new_parent_uid': None,
             'new_position': '1',
             'new_position_guid': guid,
             'new_title': None,
             'old_item': OperationItem(),
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
