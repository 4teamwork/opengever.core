from collective.transmogrifier.transmogrifier import Transmogrifier
from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_filename
from plone import api


class TestOggBundlePipeline(FunctionalTestCase):

    use_default_fixture = False

    def test_oggbundle_transmogrifier(self):
        # this is a bit hackish, but since builders currently don't work in
        # layer setup/teardown and isolation of database content is ensured
        # on a per test level we abuse just one test to setup the pipeline and
        # test its data.

        # load pipeline
        # XXX move this to a layer
        self.grant("Manager")
        user, org_unit, admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        transmogrifier = Transmogrifier(api.portal.get())
        transmogrifier.bundle_dir = resource_filename(
            'opengever.setup.tests', 'assets/oggbundle')
        transmogrifier(u'opengever.setup.oggbundle')

        # test content creation
        # XXX use separate test-cases based on a layer
        root = self.assert_repo_root_created()
        self.assert_repo_folders_created(root)

    def assert_repo_root_created(self):
        root = self.portal.get('ordnungssystem')
        self.assertEqual('Ordnungssystem', root.Title())
        self.assertEqual(u'Ordnungssystem', root.title_de)
        self.assertEqual(u'', root.title_fr)
        self.assertEqual('ordnungssystem', root.getId())
        self.assertEqual(date(2000, 1, 1), root.valid_from)
        self.assertEqual(date(2099, 12, 31), root.valid_until)
        self.assertIsNone(getattr(root, 'guid', None))
        return root

    def assert_repo_folders_created(self, root):
        folder_organisation = self.assert_organization_folder_created(root)
        self.assert_processes_folder_created(folder_organisation)
        self.assert_staff_folder_created(folder_organisation)

    def assert_organization_folder_created(self, root):
        folder_organisation = root.get('organisation')
        self.assertEqual('0. Organisation', folder_organisation.Title())
        self.assertEqual(u'Organisation', folder_organisation.title_de)
        self.assertIsNone(folder_organisation.title_fr)
        self.assertEqual('organisation', folder_organisation.getId())
        self.assertEqual(
            date(2016, 10, 1),
            ILifeCycle(folder_organisation).date_of_cassation)
        self.assertEqual(
            date(2016, 10, 2),
            ILifeCycle(folder_organisation).date_of_submission)
        self.assertEqual(
            u'unchecked',
            ILifeCycle(folder_organisation).archival_value)
        self.assertEqual(
            u'',
            ILifeCycle(folder_organisation).archival_value_annotation)
        self.assertEqual(
            u'unprotected',
            IClassification(folder_organisation).classification)
        self.assertEqual(
            30,
            ILifeCycle(folder_organisation).custody_period)
        self.assertEqual(
            date(2016, 10, 1),
            ILifeCycle(folder_organisation).date_of_cassation)
        self.assertEqual(
            date(2016, 10, 2),
            ILifeCycle(folder_organisation).date_of_submission)
        self.assertEqual(
            u'',
            folder_organisation.description)
        self.assertEqual(
            u'Aktenschrank 123',
            folder_organisation.location)
        self.assertEqual(
            u'privacy_layer_no',
            IClassification(folder_organisation).privacy_layer)
        self.assertEqual(
            u'unchecked',
            IClassification(folder_organisation).public_trial)
        self.assertEqual(
            u'',
            IClassification(folder_organisation).public_trial_statement)

        # XXX reference_number_prefix

        self.assertEqual(
            u'',
            folder_organisation.referenced_activity)
        self.assertEqual(
            5,
            ILifeCycle(folder_organisation).retention_period)
        self.assertEqual(
            date(2005, 1, 1),
            folder_organisation.valid_from)
        self.assertEqual(
            date(2030, 1, 1),
            folder_organisation.valid_until)
        self.assertEqual(
            'repositoryfolder-state-active',
            api.content.get_state(folder_organisation))
        self.assertIsNone(getattr(folder_organisation, 'guid', None))
        self.assertIsNone(getattr(folder_organisation, 'parent_guid', None))
        return folder_organisation

    def assert_processes_folder_created(self, parent):
        folder_process = parent.get('organigramm-prozesse')
        self.assertEqual('0.0. Organigramm, Prozesse', folder_process.Title())
        self.assertEqual(u'Organigramm, Prozesse', folder_process.title_de)
        self.assertIsNone(folder_process.title_fr)
        self.assertEqual('organigramm-prozesse', folder_process.getId())
        self.assertEqual(
            30,
            ILifeCycle(folder_process).custody_period)
        self.assertEqual(
            u'',
            folder_process.description)
        self.assertEqual(
            u'',
            folder_process.former_reference)
        self.assertEqual(
            u'privacy_layer_no',
            IClassification(folder_process).privacy_layer)
        self.assertEqual(
            u'unchecked',
            IClassification(folder_process).public_trial)
        self.assertEqual(
            u'',
            IClassification(folder_process).public_trial_statement)

        # XXX reference_number_prefix

        self.assertEqual(
            u'',
            folder_process.referenced_activity)
        self.assertEqual(
            5,
            ILifeCycle(folder_process).retention_period)
        self.assertEqual(
            date(2005, 1, 1),
            folder_process.valid_from)
        self.assertEqual(
            date(2020, 1, 1),
            folder_process.valid_until)
        self.assertEqual(
            'repositoryfolder-state-active',
            api.content.get_state(folder_process))
        self.assertIsNone(getattr(folder_process, 'guid', None))
        self.assertIsNone(getattr(folder_process, 'parent_guid', None))
        return folder_process

    def assert_staff_folder_created(self, parent):
        folder_staff = parent.get('personal')
        self.assertEqual('0.1. Personal', folder_staff.Title())
        self.assertEqual(u'Personal', folder_staff.title_de)
        self.assertIsNone(folder_staff.title_fr)
        self.assertEqual('personal', folder_staff.getId())
        self.assertEqual(
            u'prompt',
            ILifeCycle(folder_staff).archival_value)
        self.assertEqual(
            u'confidential',
            IClassification(folder_staff).classification)
        self.assertEqual(
            100,
            ILifeCycle(folder_staff).custody_period)
        self.assertEqual(
            u'',
            folder_staff.description)
        self.assertEqual(
            u'',
            folder_staff.former_reference)
        self.assertEqual(
            u'privacy_layer_yes',
            IClassification(folder_staff).privacy_layer)
        self.assertEqual(
            u'private',
            IClassification(folder_staff).public_trial)
        self.assertEqual(
            u'Enth\xe4lt vertrauliche Personaldossiers.',
            IClassification(folder_staff).public_trial_statement)

        # XXX reference_number_prefix

        self.assertEqual(
            u'',
            folder_staff.referenced_activity)
        self.assertEqual(
            10,
            ILifeCycle(folder_staff).retention_period)
        self.assertEqual(
            u'',
            ILifeCycle(folder_staff).retention_period_annotation)
        self.assertEqual(
            date(2005, 1, 1),
            folder_staff.valid_from)
        self.assertEqual(
            date(2050, 1, 1),
            folder_staff.valid_until)
        self.assertEqual(
            'repositoryfolder-state-active',
            api.content.get_state(folder_staff))
        self.assertIsNone(getattr(folder_staff, 'guid', None))
        self.assertIsNone(getattr(folder_staff, 'parent_guid', None))

        # XXX local roles

        return folder_staff
