from collective.transmogrifier.transmogrifier import Transmogrifier
from datetime import date
from datetime import datetime
from ftw.testing import freeze
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.interfaces import IReferenceNumber
from opengever.base.security import elevated_privileges
from opengever.bundle.console import add_guid_index
from opengever.bundle.loader import GUID_INDEX_NAME
from opengever.bundle.sections.bundlesource import BUNDLE_INGESTION_SETTINGS_KEY  # noqa
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.bundle.sections.constructor import BUNDLE_GUID_KEY
from opengever.dossier.behaviors.dossier import IDossier
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix  # noqa
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
from pkg_resources import resource_filename
from plone import api
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
from zope.component import getUtility
import json


FROZEN_NOW = datetime(2016, 12, 20, 9, 40)


class TestOggBundlePipeline(IntegrationTestCase):

    def test_oggbundle_transmogrifier(self):
        # this is a bit hackish, but since builders currently don't work in
        # layer setup/teardown and isolation of database content is ensured
        # on a per test level we abuse just one test to setup the pipeline and
        # test its data.

        self.login(self.manager)

        # Create the 'bundle_guid' index. In production, this will be done
        # by the "bin/instance import" command in opengever.bundle.console
        add_guid_index()

        # load pipeline
        transmogrifier = Transmogrifier(api.portal.get())
        annotations = IAnnotations(transmogrifier)
        annotations[BUNDLE_PATH_KEY] = resource_filename(
            'opengever.bundle.tests', 'assets/basic.oggbundle')

        unc_share_asset_directory = resource_filename(
            'opengever.bundle.tests', 'assets/files_outside_bundle')

        ingestion_settings = {
            'unc_mounts': {
                u'\\\\host\\mount': unc_share_asset_directory.decode('utf-8')
            },
        }

        # Shove ingestion settings through JSON deserialization to be as
        # close as possible to the real thing (unicode strings!).
        ingestion_settings = json.loads(json.dumps(ingestion_settings))
        annotations[BUNDLE_INGESTION_SETTINGS_KEY] = ingestion_settings

        # We need to add documents to dossiers that have already been created
        # in the 'closed' state, which isn't allowed for anyone except users
        # inheriting from `UnrestrictedUser` -> we need elevated privileges
        with freeze(FROZEN_NOW), elevated_privileges():
            transmogrifier(u'opengever.bundle.oggbundle')

        bundle = annotations[BUNDLE_KEY]

        # test content creation
        # XXX use separate test-cases based on a layer
        root = self.assert_repo_root_created()
        folder_staff = self.assert_repo_folders_created(root)
        dossier_peter = self.assert_dossiers_created(folder_staff)
        self.assert_documents_created(dossier_peter)
        self.assert_report_data_collected(bundle)

    def assert_repo_root_created(self):
        root = self.portal.get('ordnungssystem-1')
        self.assertEqual('Ordnungssystem', root.Title())
        self.assertEqual(u'Ordnungssystem', root.title_de)
        self.assertEqual(u'', root.title_fr)
        self.assertEqual(date(2000, 1, 1), root.valid_from)
        self.assertEqual(date(2099, 12, 31), root.valid_until)
        self.assertIsNone(getattr(root, 'guid', None))
        self.assert_navigation_portlet_assigned(root)
        self.assertEqual(
            IAnnotations(root)[BUNDLE_GUID_KEY],
            index_data_for(root)[GUID_INDEX_NAME])
        return root

    def assert_repo_folders_created(self, root):
        folder_organisation = self.assert_organization_folder_created(root)
        self.assert_processes_folder_created(folder_organisation)
        return self.assert_staff_folder_created(folder_organisation)

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
        self.assertEqual(
            "0",
            IReferenceNumberPrefix(folder_organisation).reference_number_prefix)
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
        self.assertEqual(
            IAnnotations(folder_organisation)[BUNDLE_GUID_KEY],
            index_data_for(folder_organisation)[GUID_INDEX_NAME])
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
        self.assertEqual(
            "0",
            IReferenceNumberPrefix(folder_process).reference_number_prefix)
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
        self.assertEqual(
            IAnnotations(folder_process)[BUNDLE_GUID_KEY],
            index_data_for(folder_process)[GUID_INDEX_NAME])
        return folder_process

    def assert_staff_folder_created(self, parent):
        folder_staff = parent.get('personal')
        self.assertEqual('0.3. Personal', folder_staff.Title())
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
        self.assertEqual(
            "3",
            IReferenceNumberPrefix(folder_staff).reference_number_prefix)
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
        self.assertEqual(
            IAnnotations(folder_staff)[BUNDLE_GUID_KEY],
            index_data_for(folder_staff)[GUID_INDEX_NAME])

        self.assertDictContainsSubset(
            {'privileged_users':
             ['Contributor', 'Reviewer', 'Editor', 'Reader'],
             'admin_users':
             ['Publisher']},
            folder_staff.__ac_local_roles__)
        self.assertTrue(folder_staff.__ac_local_roles_block__)

        return folder_staff

    def assert_dossiers_created(self, parent):
        self.assert_dossier_peter_schneider_created(parent)
        self.assert_dossier_vreni_created(parent)
        return self.assert_dossier_hanspeter_created(parent)

    def assert_dossier_peter_schneider_created(self, parent):
        dossier_peter = parent.get('dossier-18')
        self.assertEqual(
            u'Vreni Meier ist ein Tausendsassa',
            IDossier(dossier_peter).comments)
        self.assertEqual(tuple(), IDossier(dossier_peter).keywords)
        self.assertEqual(
            'Client1 0.3 / 1', IReferenceNumber(dossier_peter).get_number())
        self.assertEqual([], IDossier(dossier_peter).relatedDossier)
        self.assertEqual(u'lukas.graf', IDossier(dossier_peter).responsible)
        self.assertEqual('dossier-state-active',
                         api.content.get_state(dossier_peter))
        self.assertEqual(date(2010, 11, 11), IDossier(dossier_peter).start)
        self.assertEqual(u'Dossier Peter Schneider', dossier_peter.title)
        self.assertEqual(
            IAnnotations(dossier_peter)[BUNDLE_GUID_KEY],
            index_data_for(dossier_peter)[GUID_INDEX_NAME])

    def assert_dossier_vreni_created(self, parent):
        dossier = self.leaf_repofolder.get('dossier-20')
        self.assertEqual(u'Vreni Meier ist ein Tausendsassa',
                         IDossier(dossier).comments)
        self.assertEqual(tuple(), IDossier(dossier).keywords)
        self.assertEqual([], IDossier(dossier).relatedDossier)
        self.assertEqual(u'lukas.graf', IDossier(dossier).responsible)
        self.assertEqual('dossier-state-active',
                         api.content.get_state(dossier))
        self.assertEqual(date(2010, 11, 11), IDossier(dossier).start)
        self.assertEqual(
            u'Dossier in bestehendem Examplecontent Repository', dossier.title)
        self.assertEqual(
            IAnnotations(dossier)[BUNDLE_GUID_KEY],
            index_data_for(dossier)[GUID_INDEX_NAME])

    def assert_dossier_hanspeter_created(self, parent):
        dossier_peter = parent.get('dossier-19')
        self.assertEqual(
            u'archival worthy',
            ILifeCycle(dossier_peter).archival_value)
        self.assertEqual(
            u'Beinhaltet Informationen zum Verfahren',
            ILifeCycle(dossier_peter).archival_value_annotation)
        self.assertEqual(
            u'classified',
            IClassification(dossier_peter).classification)
        self.assertEqual(
            150,
            ILifeCycle(dossier_peter).custody_period)
        self.assertEqual(
            u'Wir haben Hanspeter M\xfcller in einem Verfahren entlassen.',
            dossier_peter.description)
        self.assertEqual(
            date(2007, 1, 1),
            IDossier(dossier_peter).start)
        self.assertEqual(
            date(2011, 1, 6),
            IDossier(dossier_peter).end)
        self.assertEqual(
            tuple(),
            IDossier(dossier_peter).keywords)
        self.assertEqual(
            u'privacy_layer_yes',
            IClassification(dossier_peter).privacy_layer)
        self.assertEqual(
            'Client1 0.3 / 7', IReferenceNumber(dossier_peter).get_number())
        self.assertEqual(
            [],
            IDossier(dossier_peter).relatedDossier)
        self.assertEqual(
            u'lukas.graf',
            IDossier(dossier_peter).responsible)
        self.assertEqual(
            5,
            ILifeCycle(dossier_peter).retention_period)
        self.assertIsNone(
            ILifeCycle(dossier_peter).retention_period_annotation)

        self.assertEqual(
            'dossier-state-resolved',
            api.content.get_state(dossier_peter))

        self.assertEqual(
            u'Hanspeter M\xfcller',
            dossier_peter.title)

        self.assertDictContainsSubset(
            {'admin_users':
                ['Contributor', 'Publisher', 'Reviewer', 'Editor', 'Reader']},
            dossier_peter.__ac_local_roles__)
        self.assertTrue(dossier_peter.__ac_local_roles_block__)

        self.assertEqual(
            IAnnotations(dossier_peter)[BUNDLE_GUID_KEY],
            index_data_for(dossier_peter)[GUID_INDEX_NAME])

        return dossier_peter

    def assert_documents_created(self, parent):
        self.assert_document_1_created(parent)
        self.assert_document_2_created(parent)
        self.assert_mail_1_created(parent)
        self.assert_mail_2_created(parent)
        self.assert_document_5_created(parent)
        self.assert_document_6_created()
        self.assert_mail_3_created()

    def assert_document_1_created(self, parent):
        document_1 = parent.objectValues()[0]

        self.assertTrue(document_1.digitally_available)
        self.assertIsNotNone(document_1.file)
        self.assertEqual(22198, len(document_1.file.data))

        self.assertEqual(
            u'david.erni',
            document_1.document_author)
        self.assertEqual(
            date(2007, 1, 1),
            document_1.document_date)
        self.assertEqual(
            tuple(),
            document_1.keywords)
        self.assertTrue(
            document_1.preserved_as_paper)
        self.assertEqual(
            [],
            document_1.relatedItems)
        self.assertEqual(
            'document-state-draft',
            api.content.get_state(document_1))
        self.assertEqual(
            u'Bewerbung Hanspeter M\xfcller',
            document_1.title)
        self.assertEqual(
            IAnnotations(document_1)[BUNDLE_GUID_KEY],
            index_data_for(document_1)[GUID_INDEX_NAME])

    def assert_document_2_created(self, parent):
        document_2 = parent.objectValues()[1]

        self.assertTrue(document_2.digitally_available)
        self.assertIsNotNone(document_2.file)
        self.assertEqual(22198, len(document_2.file.data))

        self.assertEqual(
            u'david.erni',
            document_2.document_author)
        self.assertEqual(
            date(2011, 1, 1),
            document_2.document_date)
        self.assertEqual(
            u'directive',
            document_2.document_type)
        self.assertEqual(
            tuple(),
            document_2.keywords)
        self.assertTrue(
            document_2.preserved_as_paper)
        self.assertEqual(
            u'private',
            IClassification(document_2).public_trial)
        self.assertEqual(
            u'Enth\xe4lt private Daten',
            IClassification(document_2).public_trial_statement)
        self.assertEqual(
            date(2011, 1, 1),
            document_2.receipt_date)
        self.assertEqual(
            [],
            document_2.relatedItems)
        self.assertEqual(
            'document-state-draft',
            api.content.get_state(document_2))
        self.assertEqual(
            u'Entlassung Hanspeter M\xfcller',
            document_2.title)
        self.assertEqual(
            IAnnotations(document_2)[BUNDLE_GUID_KEY],
            index_data_for(document_2)[GUID_INDEX_NAME])

    def assert_document_5_created(self, parent):
        document_5 = parent.objectValues()[4]

        self.assertTrue(document_5.digitally_available)
        self.assertIsNotNone(document_5.file)
        self.assertEqual(24390, len(document_5.file.data))

        self.assertEqual(
            'document-state-draft',
            api.content.get_state(document_5))
        self.assertEqual(
            u'Document referenced via UNC-Path',
            document_5.title)
        self.assertEqual(
            IAnnotations(document_5)[BUNDLE_GUID_KEY],
            index_data_for(document_5)[GUID_INDEX_NAME])

    def assert_document_6_created(self):
        document_6 = self.dossier.objectValues()[-2]

        self.assertTrue(document_6.digitally_available)
        self.assertIsNotNone(document_6.file)
        self.assertEqual(22198, len(document_6.file.data))
        self.assertEqual(
            'document-state-draft', api.content.get_state(document_6))
        self.assertEqual(u'Dokument in bestehendem Examplecontent Dossier',
                         document_6.title)
        self.assertEqual(
            IAnnotations(document_6)[BUNDLE_GUID_KEY],
            index_data_for(document_6)[GUID_INDEX_NAME])

    def assert_mail_1_created(self, parent):
        mail = parent.objectValues()[2]

        self.assertTrue(mail.digitally_available)
        self.assertIsNotNone(mail.message)
        self.assertEqual(920, len(mail.message.data))

        self.assertEqual(
            u'Peter Muster <from@example.org>',
            mail.document_author)
        self.assertEqual(
            date(2013, 1, 1),
            mail.document_date)
        self.assertEqual(
            None,
            mail.document_type)
        self.assertEqual(
            tuple(),
            mail.keywords)
        self.assertTrue(
            mail.preserved_as_paper)
        self.assertEqual(
            u'unchecked',
            IClassification(mail).public_trial)
        self.assertEqual(
            u'',
            IClassification(mail).public_trial_statement)
        self.assertEqual(
            FROZEN_NOW.date(),
            mail.receipt_date)
        self.assertEqual(
            'mail-state-active',
            api.content.get_state(mail))

        self.assertEqual(
            u'Ein Mail',
            mail.title)
        self.assertEqual(
            IAnnotations(mail)[BUNDLE_GUID_KEY],
            index_data_for(mail)[GUID_INDEX_NAME])

    def assert_mail_2_created(self, parent):
        mail = parent.objectValues()[3]

        self.assertIsNotNone(mail.message)
        self.assertEqual(920, len(mail.message.data))
        self.assertEqual(u'Lorem Ipsum', mail.title)
        self.assertEqual(
            IAnnotations(mail)[BUNDLE_GUID_KEY],
            index_data_for(mail)[GUID_INDEX_NAME])

    def assert_mail_3_created(self):
        mail = self.dossier.objectValues()[-1]

        self.assertIsNotNone(mail.message)
        self.assertEqual(920, len(mail.message.data))
        self.assertEqual(
            u'Mail in bestehendem Examplecontent Dossier', mail.title)
        self.assertEqual(
            IAnnotations(mail)[BUNDLE_GUID_KEY],
            index_data_for(mail)[GUID_INDEX_NAME])

    def assert_report_data_collected(self, bundle):
        report_data = bundle.report_data
        metadata = report_data['metadata']

        self.assertSetEqual(
            set([
                'opengever.repository.repositoryroot',
                'opengever.repository.repositoryfolder',
                'opengever.dossier.businesscasedossier',
                'opengever.document.document',
                'ftw.mail.mail']),
            set(metadata.keys()))

        reporoots = metadata['opengever.repository.repositoryroot']
        repofolders = metadata['opengever.repository.repositoryfolder']
        dossiers = metadata['opengever.dossier.businesscasedossier']
        documents = metadata['opengever.document.document']
        mails = metadata['ftw.mail.mail']

        self.assertEqual(1, len(reporoots))
        self.assertEqual(3, len(repofolders))
        self.assertEqual(3, len(dossiers))
        self.assertEqual(5, len(documents))
        self.assertEqual(3, len(mails))

    def assert_navigation_portlet_assigned(self, root):
        manager = getUtility(
            IPortletManager, name=u'plone.leftcolumn', context=root)
        mapping = getMultiAdapter(
            (root, manager,), IPortletAssignmentMapping)
        tree_portlet_assignment = mapping.get(
            'opengever-portlets-tree-TreePortlet')
        self.assertEqual('ordnungssystem-1', tree_portlet_assignment.root_path)
