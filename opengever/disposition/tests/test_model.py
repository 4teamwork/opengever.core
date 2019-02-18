from datetime import date
from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import staticuid
from opengever.base.behaviors.classification import IClassification
from opengever.disposition.ech0160.model import ContentRootFolder
from opengever.disposition.ech0160.model import Document
from opengever.disposition.ech0160.model import Dossier
from opengever.disposition.ech0160.model import File
from opengever.disposition.ech0160.model import Position
from opengever.disposition.ech0160.model import Repository
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from plone import api
import hashlib
import unittest


class TestRepositoryModel(IntegrationTestCase):

    def test_add_complete_repository_folder_path_for_each_added_dossier(self):
        self.login(self.regular_user)
        dossier = create(Builder('dossier').within(self.empty_repofolder))

        model = Repository()
        model.add_dossier(Dossier(self.dossier))

        self.assertEquals(self.repository_root, model.obj)
        positions = model.positions.values()

        self.assertEquals([self.branch_repofolder], [pos.obj for pos in positions])
        self.assertEquals([self.leaf_repofolder],
                          [pos.obj for pos in positions[0].positions.values()])

        model.add_dossier(Dossier(dossier))
        positions = model.positions.values()

        self.assertEquals(set([self.branch_repofolder, self.empty_repofolder]),
                          set([pos.obj for pos in positions]))

    def test_name_is_root_title(self):
        self.login(self.regular_user)
        model = Repository()
        model.obj = self.repository_root

        self.assertEquals(self.repository_root.Title(), model.binding().name)

    def test_anwendungszeitraum_von_is_valid_from_date_or_keine_angabe(self):
        self.login(self.regular_user)
        model = Repository()
        model.obj = self.repository_root

        self.repository_root.valid_until = date(2016, 7, 11)
        self.assertEquals(date(2016, 7, 11),
                          model.binding().anwendungszeitraum.bis.datum.date())
        self.assertEquals('keine Angabe',
                          model.binding().anwendungszeitraum.von.datum)

        self.repository_root.valid_from = date(2016, 6, 11)
        self.assertEquals(date(2016, 6, 11),
                          model.binding().anwendungszeitraum.von.datum.date())


class TestPositionModel(IntegrationTestCase):

    def test_id_is_uid_prefixed_with_a_underscore(self):
        self.login(self.regular_user)

        model = Position(self.branch_repofolder)
        self.assertEquals('_createrepositorytree000000000002', model.binding().id)

    def test_nummer_is_reference_number(self):
        self.login(self.regular_user)

        model = Position(self.leaf_repofolder)
        self.assertEquals('1.1', model.binding().nummer)

    def test_titel_is_repository_title_without_reference_number(self):
        self.login(self.regular_user)

        model = Position(self.leaf_repofolder)
        self.assertEquals(u'Vertr\xe4ge und Vereinbarungen', model.binding().titel)

    def test_classification_attributes_and_schutzfrist(self):
        self.login(self.regular_user)

        classification = IClassification(self.leaf_repofolder)
        classification.privacy_layer = 'privacy_layer_yes'
        classification.public_trial = 'private'
        classification.public_trial_statement = u'Enth\xe4lt sch\xfctzenswerte Daten.'

        model = Position(self.leaf_repofolder)
        binding = model.binding()

        self.assertEquals(u'30', binding.schutzfrist)
        self.assertEquals('unprotected', binding.klassifizierungskategorie)
        self.assertEquals(1, binding.datenschutz)
        self.assertEquals('private', binding.oeffentlichkeitsstatus)
        self.assertEquals(u'Enth\xe4lt sch\xfctzenswerte Daten.',
                          binding.oeffentlichkeitsstatusBegruendung)

    def test_add_repository_folders_descendants_as_ordnunssystempositionen(self):
        self.login(self.regular_user)

        model = Position(self.branch_repofolder)
        model._add_descendants([self.leaf_repofolder])

        self.assertEquals([self.leaf_repofolder],
                          [pos.obj for pos in model.positions.values()])

    def test_add_dossier_descendants_as_dossiers(self):
        self.login(self.regular_user)

        dossier_model = Dossier(self.dossier)
        model = Position(self.leaf_repofolder)
        model._add_descendants([dossier_model])

        self.assertEquals([dossier_model], model.dossiers.values())


class TestDossier(IntegrationTestCase):

    @staticuid('fake')
    def test_id_is_uid_prefixed_with_a_underscore(self):
        self.login(self.regular_user)

        self.assertEquals(u'_createtreatydossiers000000000001',
                          Dossier(self.dossier).binding().id)

    def test_titel_is_title_in_unicode(self):
        self.login(self.regular_user)

        self.assertEquals(self.dossier.Title().decode("utf-8"),
                          Dossier(self.dossier).binding().titel)

    def test_aktenzeichen_is_refernce_number(self):
        self.login(self.regular_user)

        self.assertEquals('Client1 1.1 / 1',
                          Dossier(self.dossier).binding().aktenzeichen)

    def test_classification_attributes_and_schutzfrist(self):
        self.login(self.regular_user)

        classification = IClassification(self.dossier)
        classification.privacy_layer = 'privacy_layer_yes'
        classification.public_trial = 'private'
        classification.public_trial_statement = u'Enth\xe4lt sch\xfctzenswerte Daten.'

        binding = Dossier(self.dossier).binding()

        self.assertEquals(u'30', binding.schutzfrist)
        self.assertEquals('unprotected', binding.klassifizierungskategorie)
        self.assertEquals(1, binding.datenschutz)
        self.assertEquals('private', binding.oeffentlichkeitsstatus)
        self.assertEquals(u'Enth\xe4lt sch\xfctzenswerte Daten.',
                          binding.oeffentlichkeitsstatusBegruendung)

    def test_entstehungszeitraum_is_oldest_document_date_to_newest_one(self):
        self.login(self.regular_user)

        create(Builder('document')
               .within(self.empty_dossier)
               .with_modification_date(DateTime(2016, 1, 15))
               .with_creation_date(DateTime(2014, 3, 4)))
        create(Builder('document')
               .within(self.empty_dossier)
               .with_modification_date(DateTime(2016, 3, 1))
               .with_creation_date(DateTime(2015, 1, 1)))
        create(Builder('document')
               .within(self.empty_dossier)
               .with_modification_date(DateTime(2016, 12, 27))
               .with_creation_date(DateTime(2016, 1, 1)))

        binding = Dossier(self.empty_dossier).binding()

        self.assertEquals(date(2014, 3, 4),
                          binding.entstehungszeitraum.von.datum.date())
        self.assertEquals(date(2016, 12, 27),
                          binding.entstehungszeitraum.bis.datum.date())

    def test_entstehungszeitraum_is_kein_angabe_when_dossier_is_empty(self):
        self.login(self.regular_user)

        binding = Dossier(self.empty_dossier).binding()
        self.assertEquals(u'keine Angabe',
                          binding.entstehungszeitraum.von.datum)
        self.assertEquals(u'keine Angabe',
                          binding.entstehungszeitraum.bis.datum)

    def test_eroeffnungsdatum_is_start_date(self):
        self.login(self.regular_user)

        binding = Dossier(self.dossier).binding()
        self.assertEquals(IDossier(self.dossier).start,
                          binding.eroeffnungsdatum.datum.date())

    def test_abschlussdatum_is_end_date(self):
        self.login(self.regular_user)

        binding = Dossier(self.inactive_dossier).binding()
        self.assertEquals(date(2016, 12, 31),
                          binding.abschlussdatum.datum.date())

    def test_add_descendants_adds_all_subdossiers(self):
        self.login(self.regular_user)

        model = Dossier(self.dossier)
        model._add_descendants()

        self.assertEquals(
            set([self.subdossier, self.subdossier2]),
            set([mod.obj for mod in model.dossiers.values()]))

    def test_add_descendants_adds_all_containing_documents(self):
        self.login(self.manager)

        model = Dossier(self.dossier)
        model._add_descendants()

        brains = api.content.find(context=self.dossier, depth=1,
                                  portal_type='opengever.document.document')
        expected_documents = set([brain.getObject() for brain in brains])

        self.assertEquals(expected_documents,
                          set([doc.obj for doc in model.documents.values()]))

    @unittest.skip('Currently not implemented')
    def test_add_descendants_adds_also_documents_in_tasks(self):
        """If this were implemented it would show up in the test
        test_add_descendants_adds_all_containing_documents
        """
        self.login(self.regular_user)
        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))
        document = create(Builder('document').within(task))

        model = Dossier(dossier)
        model._add_descendants()

        self.assertEqual(
            set([document]),
            set([doc.obj for doc in model.documents.values()]))


class TestDocumentModel(IntegrationTestCase):

    def test_title_is_document_title_in_unicode(self):
        self.login(self.regular_user)

        self.assertEquals(self.document.Title().decode("utf-8"),
                          Document(self.document).binding().titel)

    def test_autor_is_a_list_containing_document_author(self):
        self.login(self.regular_user)

        self.assertEquals(['test_user_1_'],
                          [author for author in Document(self.document).binding().autor])

    def test_erscheinungsform_is_digital_available_flag(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'digital',
            Document(self.document).binding().erscheinungsform)

        self.assertEquals(
            u'nicht digital',
            Document(self.empty_document).binding().erscheinungsform)

    def test_dokumentyp_is_document_type_title(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'Contract',
            Document(self.document).binding().dokumenttyp)

    def test_registrierdatum_is_created_date(self):
        self.login(self.regular_user)

        self.assertEquals(
            self.document.created().asdatetime().date(),
            Document(self.document).binding().registrierdatum.datum.date())

    def test_entstehungszeitraum_is_created_to_modified_date_range(self):
        self.login(self.regular_user)

        self.document.creation_date = DateTime(2016, 11, 6)
        self.document.modification_date = DateTime(2017, 12, 6)

        entstehungszeitraum = Document(self.document).binding().entstehungszeitraum
        self.assertEquals(date(2016, 11, 6), entstehungszeitraum.von.datum.date())
        self.assertEquals(date(2017, 12, 6), entstehungszeitraum.bis.datum.date())


class TestFolderAndFileModel(IntegrationTestCase):

    def test_complete_tree_representation(self):
        self.login(self.regular_user)

        repo = Repository()
        content = ContentRootFolder('SIP_20101212_FD_10xy')

        models = [Dossier(self.dossier), Dossier(self.inactive_dossier)]
        for dossier_model in models:
            repo.add_dossier(dossier_model)
            content.add_dossier(dossier_model)

        self.assertEquals(2, len(content.folders))
        dossier_model, inactive_dossier_model = content.folders

        # self.dossier
        # two subdossiers, self.subdossier and self.subdossier2
        self.assertEquals(2, len(dossier_model.folders))
        # dossier a contains two files, one for self.document
        # and one automatically generated for self.decided_proposal
        self.assertEquals(2, len(dossier_model.files))
        subdossier_model = dossier_model.folders[0]
        subdossier2_model = dossier_model.folders[1]

        # self.subdossier
        # contains self.subsubdossier
        self.assertEquals(1, len(subdossier_model.folders))
        self.assertEquals(1, len(subdossier_model.files))
        subdocument_model = subdossier_model.files[0]
        self.assertEquals(self.subdocument.get_filename(), subdocument_model.filename)
        self.assertEquals(self.subdocument.file._blob.committed(), subdocument_model.filepath)

        # self.subsubdossier
        subsubdossier_model = subdossier_model.folders[0]
        self.assertEquals([], subsubdossier_model.folders)
        self.assertEquals(1, len(subsubdossier_model.files))

        # self.subdossier2
        self.assertEquals([], subdossier2_model.folders)
        self.assertEquals(0, len(subdossier2_model.files))

        # self.inactive_dossier
        self.assertEquals([], inactive_dossier_model.folders)
        self.assertEquals(1, len(inactive_dossier_model.files))
        inactive_document_model = inactive_dossier_model.files[0]
        self.assertEquals(self.inactive_document.get_filename(), inactive_document_model.filename)
        self.assertEquals(self.inactive_document.file._blob.committed(), inactive_document_model.filepath)


class TestFileModel(IntegrationTestCase):

    def setUp(self):
        super(TestFileModel, self).setUp()
        self.toc = ContentRootFolder('FAKE_PATH')
        self.toc.next_file = 3239

    def test_uses_documents_archival_file_if_exist(self):
        self.login(self.regular_user)

        model = File(self.toc, Document(self.expired_document))

        self.assertEquals(u'test.pdf', model.filename)
        self.assertEquals(self.expired_document.archival_file._blob.committed(),
                          model.filepath)

    def test_represents_documents_file_if_no_archival_file_exist(self):
        self.login(self.regular_user)

        model = File(self.toc, Document(self.document))

        self.assertEquals(u'Vertraegsentwurf.docx', model.filename)
        self.assertEquals(self.document.file._blob.committed(), model.filepath)

    def test_named_next_file_number_prefixed_with_p(self):
        self.login(self.regular_user)

        model = File(self.toc, Document(self.document))
        self.assertEquals('p003239.docx', model.name)
        model = File(self.toc, Document(self.expired_document))
        self.assertEquals('p003240.pdf', model.name)

    def test_pruefsumme_is_a_md5_hash(self):
        self.login(self.regular_user)

        model = File(self.toc, Document(self.expired_document))

        _hash = hashlib.md5()
        _hash.update('TEST')

        self.assertEquals(_hash.hexdigest(), model.binding().pruefsumme)
        self.assertEquals('MD5', model.binding().pruefalgorithmus)
