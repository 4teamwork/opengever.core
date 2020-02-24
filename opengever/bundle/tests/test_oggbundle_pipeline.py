from collective.transmogrifier.transmogrifier import Transmogrifier
from datetime import date
from datetime import datetime
from DateTime import DateTime
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
import pytz
import tzlocal


FROZEN_NOW = datetime(2016, 12, 20, 9, 40)


class TestOggBundlePipeline(IntegrationTestCase):

    def find_by_title(self, parent, title):
        matching_children = [child for child in parent.objectValues()
                             if getattr(child, "title", None) == title]
        for child in parent.objectValues():
            object_title = getattr(child, "title", None)
            if object_title == title:
                return child

        self.assertTrue(
            matching_children,
            msg="did not find object with title: {}".format(title))
        self.assertEqual(
            1, len(matching_children),
            msg="found more than one object with title: {}".format(title))
        return matching_children[0]

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

        # The structure of the imported bundle is as follows
        # * reporoot: Ordnungssystem
        #     * branch_repofolder: Organisation
        #         * leaf_repofolder: Personal
        #             * empty_dossier: Dossier Peter Schneider
        #             * dossier: Hanspeter Muller
        #                 * document1: Bewerbung Hanspeter Muller
        #                 * document2: Entlassung Hanspeter Muller
        #                 * mail1: Ein Mail
        #                 * mail2: Mail without title
        #                 * document3: Document referenced via UNC-Path
        #                 * document4: Nonexistent document referenced via UNC-Path with Umlaut
        #         * empty_repofolder: Organigramm, Prozesse
        #
        # Some more elements get imported in existing positions from the
        # the fixture. Where they will be imported can change when elements
        # are added in the fixture.
        # * dossier2 (in position 1.1, i.e. self.leaf_repofolder): Dossier in bestehendem Examplecontent Repository
        # * document5 (in position 1.1 / 1 i.e. self.dossier): Dokument in bestehendem Examplecontent Dossier
        # * mail3 (in position 1.1 / 1 i.e. self.dossier): : Mail in bestehendem Examplecontent Dossier

        reporoot = self.assert_reporoot_created()
        branch_repofolder = self.assert_organization_folder_created(reporoot)
        self.assert_empty_repofolder_created(branch_repofolder)
        leaf_repofolder = self.assert_leaf_repofolder_created(branch_repofolder)

        self.assert_empty_dossier_created(leaf_repofolder)
        self.assert_dossier2_created()
        dossier = self.assert_dossier_created(leaf_repofolder)

        self.assert_document1_created(dossier)
        self.assert_document2_created(dossier)
        self.assert_mail1_created(dossier)
        self.assert_mail2_created(dossier)
        self.assert_document3_created(dossier)
        self.assert_document4_created(dossier)
        self.assert_document5_created()
        self.assert_mail3_created()

        self.assert_report_data_collected(bundle)

    def assert_reporoot_created(self):
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

    def assert_empty_repofolder_created(self, parent):
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

    def assert_leaf_repofolder_created(self, parent):
        leaf_repofolder = parent.get('personal')
        self.assertEqual('0.3. Personal', leaf_repofolder.Title())
        self.assertEqual(u'Personal', leaf_repofolder.title_de)
        self.assertIsNone(leaf_repofolder.title_fr)
        self.assertEqual('personal', leaf_repofolder.getId())
        self.assertEqual(
            u'prompt',
            ILifeCycle(leaf_repofolder).archival_value)
        self.assertEqual(
            u'confidential',
            IClassification(leaf_repofolder).classification)
        self.assertEqual(
            100,
            ILifeCycle(leaf_repofolder).custody_period)
        self.assertEqual(
            u'',
            leaf_repofolder.description)
        self.assertEqual(
            u'',
            leaf_repofolder.former_reference)
        self.assertEqual(
            u'privacy_layer_yes',
            IClassification(leaf_repofolder).privacy_layer)
        self.assertEqual(
            u'private',
            IClassification(leaf_repofolder).public_trial)
        self.assertEqual(
            u'Enth\xe4lt vertrauliche Personaldossiers.',
            IClassification(leaf_repofolder).public_trial_statement)
        self.assertEqual(
            "3",
            IReferenceNumberPrefix(leaf_repofolder).reference_number_prefix)
        self.assertEqual(
            u'',
            leaf_repofolder.referenced_activity)
        self.assertEqual(
            10,
            ILifeCycle(leaf_repofolder).retention_period)
        self.assertEqual(
            u'',
            ILifeCycle(leaf_repofolder).retention_period_annotation)
        self.assertEqual(
            date(2005, 1, 1),
            leaf_repofolder.valid_from)
        self.assertEqual(
            date(2050, 1, 1),
            leaf_repofolder.valid_until)
        self.assertEqual(
            'repositoryfolder-state-active',
            api.content.get_state(leaf_repofolder))
        self.assertIsNone(getattr(leaf_repofolder, 'guid', None))
        self.assertIsNone(getattr(leaf_repofolder, 'parent_guid', None))
        self.assertEqual(
            IAnnotations(leaf_repofolder)[BUNDLE_GUID_KEY],
            index_data_for(leaf_repofolder)[GUID_INDEX_NAME])

        self.assertDictContainsSubset(
            {'privileged_users':
             ['Contributor', 'Reviewer', 'Editor', 'Reader'],
             'admin_users':
             ['Publisher']},
            leaf_repofolder.__ac_local_roles__)
        self.assertTrue(leaf_repofolder.__ac_local_roles_block__)

        return leaf_repofolder

    def assert_empty_dossier_created(self, parent):
        dossier = self.find_by_title(parent, "Dossier Peter Schneider")

        self.assertEqual(
            u'Vreni Meier ist ein Tausendsassa',
            IDossier(dossier).comments)
        self.assertEqual(tuple(), IDossier(dossier).keywords)
        self.assertEqual(
            'Client1 0.3 / 1', IReferenceNumber(dossier).get_number())
        self.assertEqual([], IDossier(dossier).relatedDossier)
        self.assertEqual(u'lukas.graf', IDossier(dossier).responsible)
        self.assertEqual('dossier-state-active',
                         api.content.get_state(dossier))
        self.assertEqual(date(2010, 11, 11), IDossier(dossier).start)
        self.assertEqual(
            IAnnotations(dossier)[BUNDLE_GUID_KEY],
            index_data_for(dossier)[GUID_INDEX_NAME])

    def assert_dossier2_created(self):
        dossier = self.find_by_title(
            self.leaf_repofolder,
            u'Dossier in bestehendem Examplecontent Repository')

        self.assertEqual(u'Vreni Meier ist ein Tausendsassa',
                         IDossier(dossier).comments)
        self.assertEqual(tuple(), IDossier(dossier).keywords)
        self.assertEqual([], IDossier(dossier).relatedDossier)
        self.assertEqual(u'lukas.graf', IDossier(dossier).responsible)
        self.assertEqual('dossier-state-active',
                         api.content.get_state(dossier))
        self.assertEqual(date(2010, 11, 11), IDossier(dossier).start)
        self.assertEqual(
            IAnnotations(dossier)[BUNDLE_GUID_KEY],
            index_data_for(dossier)[GUID_INDEX_NAME])

    def assert_dossier_created(self, parent):
        dossier = self.find_by_title(parent, u'Hanspeter M\xfcller')

        self.assertEqual(
            u'archival worthy',
            ILifeCycle(dossier).archival_value)
        self.assertEqual(
            u'Beinhaltet Informationen zum Verfahren',
            ILifeCycle(dossier).archival_value_annotation)
        self.assertEqual(
            u'classified',
            IClassification(dossier).classification)
        self.assertEqual(
            150,
            ILifeCycle(dossier).custody_period)
        self.assertEqual(
            u'Wir haben Hanspeter M\xfcller in einem Verfahren entlassen.',
            dossier.description)
        self.assertEqual(
            date(2007, 1, 1),
            IDossier(dossier).start)
        self.assertEqual(
            date(2011, 1, 6),
            IDossier(dossier).end)
        self.assertEqual(
            tuple(),
            IDossier(dossier).keywords)
        self.assertEqual(
            u'privacy_layer_yes',
            IClassification(dossier).privacy_layer)
        self.assertEqual(
            'Client1 0.3 / 7', IReferenceNumber(dossier).get_number())
        self.assertEqual(
            [],
            IDossier(dossier).relatedDossier)
        self.assertEqual(
            u'lukas.graf',
            IDossier(dossier).responsible)
        self.assertEqual(
            5,
            ILifeCycle(dossier).retention_period)
        self.assertIsNone(
            ILifeCycle(dossier).retention_period_annotation)

        self.assertEqual(
            'dossier-state-resolved',
            api.content.get_state(dossier))

        self.assertDictContainsSubset(
            {'admin_users':
                ['Contributor', 'Publisher', 'Reviewer', 'Editor', 'Reader']},
            dossier.__ac_local_roles__)
        self.assertTrue(dossier.__ac_local_roles_block__)

        self.assertEqual(
            IAnnotations(dossier)[BUNDLE_GUID_KEY],
            index_data_for(dossier)[GUID_INDEX_NAME])

        return dossier

    def assert_document1_created(self, parent):
        document1 = self.find_by_title(parent, u'Bewerbung Hanspeter M\xfcller')

        self.assertTrue(document1.digitally_available)
        self.assertIsNotNone(document1.file)
        self.assertEqual(22198, len(document1.file.data))

        self.assertEqual(
            u'david.erni',
            document1.document_author)
        self.assertEqual(
            date(2007, 1, 1),
            document1.document_date)
        self.assertEqual(
            document1.modified(),
            DateTime("2019-12-05T14:09:59.240726"))
        self.assertEqual(
            document1.changed,
            datetime(2019, 12, 5, 14, 9, 59, 240726, tzinfo=tzlocal.get_localzone()))

        self.assertEqual(
            tuple(),
            document1.keywords)
        self.assertTrue(
            document1.preserved_as_paper)
        self.assertEqual(
            [],
            document1.relatedItems)
        self.assertEqual(
            'document-state-draft',
            api.content.get_state(document1))
        self.assertEqual(
            IAnnotations(document1)[BUNDLE_GUID_KEY],
            index_data_for(document1)[GUID_INDEX_NAME])

    def assert_document2_created(self, parent):
        document2 = self.find_by_title(parent, u'Entlassung Hanspeter M\xfcller')

        self.assertTrue(document2.digitally_available)
        self.assertIsNotNone(document2.file)
        self.assertEqual(22198, len(document2.file.data))

        self.assertEqual(
            u'david.erni',
            document2.document_author)
        self.assertEqual(
            date(2011, 1, 1),
            document2.document_date)
        self.assertEqual(
            document2.modified(),
            DateTime("2019-12-05"))
        self.assertEqual(
            document2.changed,
            datetime(2019, 12, 5, tzinfo=tzlocal.get_localzone()))

        self.assertEqual(
            u'directive',
            document2.document_type)
        self.assertEqual(
            tuple(),
            document2.keywords)
        self.assertTrue(
            document2.preserved_as_paper)
        self.assertEqual(
            u'private',
            IClassification(document2).public_trial)
        self.assertEqual(
            u'Enth\xe4lt private Daten',
            IClassification(document2).public_trial_statement)
        self.assertEqual(
            date(2011, 1, 1),
            document2.receipt_date)
        self.assertEqual(
            [],
            document2.relatedItems)
        self.assertEqual(
            'document-state-draft',
            api.content.get_state(document2))
        self.assertEqual(
            IAnnotations(document2)[BUNDLE_GUID_KEY],
            index_data_for(document2)[GUID_INDEX_NAME])

    def assert_document3_created(self, parent):
        document3 = self.find_by_title(parent, u'Document referenced via UNC-Path')

        self.assertTrue(document3.digitally_available)
        self.assertIsNotNone(document3.file)
        self.assertEqual(24390, len(document3.file.data))

        self.assertEqual(
            'document-state-draft',
            api.content.get_state(document3))
        self.assertEqual(
            IAnnotations(document3)[BUNDLE_GUID_KEY],
            index_data_for(document3)[GUID_INDEX_NAME])

        self.assertEqual(
            document3.modified(),
            DateTime(FROZEN_NOW))
        self.assertEqual(
            document3.changed,
            pytz.utc.localize(FROZEN_NOW))
        self.assertEqual(
            document3.created(),
            DateTime(FROZEN_NOW))

    def assert_document4_created(self, parent):
        document4 = self.find_by_title(
            parent, u'Nonexistent document referenced via UNC-Path with Umlaut')

        self.assertFalse(document4.digitally_available)
        self.assertIsNone(document4.file)

        self.assertEqual(
            'document-state-draft',
            api.content.get_state(document4))
        self.assertEqual(
            IAnnotations(document4)[BUNDLE_GUID_KEY],
            index_data_for(document4)[GUID_INDEX_NAME])

    def assert_document5_created(self):
        document5 = self.find_by_title(
            self.dossier, u'Dokument in bestehendem Examplecontent Dossier')

        self.assertTrue(document5.digitally_available)
        self.assertIsNotNone(document5.file)
        self.assertEqual(22198, len(document5.file.data))
        self.assertEqual(
            'document-state-draft', api.content.get_state(document5))
        self.assertEqual(
            IAnnotations(document5)[BUNDLE_GUID_KEY],
            index_data_for(document5)[GUID_INDEX_NAME])

    def assert_mail1_created(self, parent):
        mail = self.find_by_title(parent, u'Ein Mail')

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
            IAnnotations(mail)[BUNDLE_GUID_KEY],
            index_data_for(mail)[GUID_INDEX_NAME])

    def assert_mail2_created(self, parent):
        mail = self.find_by_title(parent, u'Lorem Ipsum')

        self.assertIsNotNone(mail.message)
        self.assertEqual(920, len(mail.message.data))
        self.assertEqual(
            IAnnotations(mail)[BUNDLE_GUID_KEY],
            index_data_for(mail)[GUID_INDEX_NAME])

    def assert_mail3_created(self):
        mail = self.find_by_title(
            self.dossier, u'Mail in bestehendem Examplecontent Dossier')

        self.assertIsNotNone(mail.message)
        self.assertEqual(920, len(mail.message.data))
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
        self.assertEqual(4, len(mails))

    def assert_navigation_portlet_assigned(self, root):
        manager = getUtility(
            IPortletManager, name=u'plone.leftcolumn', context=root)
        mapping = getMultiAdapter(
            (root, manager,), IPortletAssignmentMapping)
        tree_portlet_assignment = mapping.get(
            'opengever-portlets-tree-TreePortlet')
        self.assertEqual('ordnungssystem-1', tree_portlet_assignment.root_path)
