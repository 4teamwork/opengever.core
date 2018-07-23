from datetime import date
from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import staticuid
from opengever.disposition.ech0160.model import ContentRootFolder
from opengever.disposition.ech0160.model import Document
from opengever.disposition.ech0160.model import Dossier
from opengever.disposition.ech0160.model import File
from opengever.disposition.ech0160.model import Position
from opengever.disposition.ech0160.model import Repository
from opengever.testing import FunctionalTestCase
import hashlib
import unittest


class TestRepositoryModel(FunctionalTestCase):

    def test_add_complete_repository_folder_path_for_each_added_dossier(self):
        root = create(Builder('repository_root'))
        folder1 = create(Builder('repository').within(root))
        folder1_1 = create(Builder('repository').within(folder1))
        dossier1 = create(Builder('dossier').within(folder1_1))
        folder2 = create(Builder('repository').within(root))
        dossier2 = create(Builder('dossier').within(folder2))
        folder3 = create(Builder('repository').within(root))
        create(Builder('dossier').within(folder3))

        model = Repository()
        model.add_dossier(Dossier(dossier1))

        self.assertEquals(root, model.obj)
        positions = model.positions.values()

        self.assertEquals([folder1], [pos.obj for pos in positions])
        self.assertEquals([folder1_1],
                          [pos.obj for pos in positions[0].positions.values()])

        model.add_dossier(Dossier(dossier2))
        positions = model.positions.values()

        self.assertEquals(set([folder1, folder2]),
                          set([pos.obj for pos in positions]))

    def test_name_is_root_title(self):
        root = create(Builder('repository_root').titled(u'Ordnungsystem 2001'))

        model = Repository()
        model.obj = root

        self.assertEquals(u'Ordnungsystem 2001', model.binding().name)

    def test_anwendungszeitraum_bis_is_valid_from_date_or_keine_angabe(self):
        root1 = create(Builder('repository_root')
                       .having(valid_from=date(2016, 6, 11)))
        model = Repository()
        model.obj = root1
        self.assertEquals(date(2016, 6, 11),
                          model.binding().anwendungszeitraum.von.datum.date())

        root2 = create(Builder('repository_root')
                       .having(valid_until=date(2016, 6, 11)))
        model = Repository()
        model.obj = root2
        self.assertEquals('keine Angabe',
                          model.binding().anwendungszeitraum.von.datum)


class TestPositionModel(FunctionalTestCase):

    @staticuid('fake')
    def test_id_is_uid_prefixed_with_a_underscore(self):
        folder = create(Builder('repository'))
        model = Position(folder)

        self.assertEquals('_fake0000000000000000000000000001', model.binding().id)

    def test_nummer_is_reference_number(self):
        folder1 = create(Builder('repository'))
        folder1_7 = create(Builder('repository')
                           .having(reference_number_prefix='7')
                           .within(folder1))
        model = Position(folder1_7)

        self.assertEquals('1.7', model.binding().nummer)

    def test_titel_is_repository_title_without_reference_number(self):
        folder = create(Builder('repository').titled(u'Qualit\xe4tsumfragen'))
        model = Position(folder)

        self.assertEquals(u'Qualit\xe4tsumfragen', model.binding().titel)

    def test_classification_attributes_and_schutzfrist(self):
        folder = create(Builder('repository')
                        .having(custody_period=30,
                                classification='unprotected',
                                privacy_layer='privacy_layer_yes',
                                public_trial='private',
                                public_trial_statement=u'Enth\xe4lt sch\xfctzenswerte Daten.')
                        .titled(u'Qualit\xe4tsumfragen'))

        model = Position(folder)
        binding = model.binding()

        self.assertEquals(u'30', binding.schutzfrist)
        self.assertEquals('unprotected', binding.klassifizierungskategorie)
        self.assertEquals(1, binding.datenschutz)
        self.assertEquals('private', binding.oeffentlichkeitsstatus)
        self.assertEquals(u'Enth\xe4lt sch\xfctzenswerte Daten.',
                          binding.oeffentlichkeitsstatusBegruendung)

    def test_add_repository_folders_descendants_as_ordnunssystempositionen(self):
        folder = create(Builder('repository'))
        folder_1 = create(Builder('repository').within(folder))

        model = Position(folder)
        model._add_descendants([folder_1])

        self.assertEquals(
            [folder_1],
            [pos.obj for pos in model.positions.values()])

    def test_add_dossier_descendants_as_dossiers(self):
        folder = create(Builder('repository'))
        dossier = create(Builder('dossier').within(folder))
        dossier_model = Dossier(dossier)

        model = Position(folder)
        model._add_descendants([dossier_model])

        self.assertEquals([dossier_model], model.dossiers.values())


class TestDossierModel(FunctionalTestCase):

    @staticuid('fake')
    def test_id_is_uid_prefixed_with_a_underscore(self):
        dossier = create(Builder('dossier'))
        self.assertEquals('_fake0000000000000000000000000001',
                          Dossier(dossier).binding().id)

    def test_titel_is_title_in_utf8(self):
        dossier = create(Builder('dossier').titled(u'F\xfchrung'))
        self.assertEquals(u'F\xfchrung', Dossier(dossier).binding().titel)

    def test_aktenzeichen_is_refernce_number(self):
        folder1 = create(Builder('repository'))
        folder1_7 = create(Builder('repository')
                           .having(reference_number_prefix='7')
                           .within(folder1))
        dossier = create(Builder('dossier').within(folder1_7))

        self.assertEquals('Client1 1.7 / 1', Dossier(dossier).binding().aktenzeichen)

    def test_classification_attributes_and_schutzfrist(self):
        dossier = create(Builder('dossier')
                         .having(custody_period=30,
                                 classification='unprotected',
                                 privacy_layer='privacy_layer_yes',
                                 public_trial='private',
                                 public_trial_statement=u'Enth\xe4lt sch\xfctzenswerte Daten.'))

        binding = Dossier(dossier).binding()

        self.assertEquals(u'30', binding.schutzfrist)
        self.assertEquals('unprotected', binding.klassifizierungskategorie)
        self.assertEquals(1, binding.datenschutz)
        self.assertEquals('private', binding.oeffentlichkeitsstatus)
        self.assertEquals(u'Enth\xe4lt sch\xfctzenswerte Daten.',
                          binding.oeffentlichkeitsstatusBegruendung)

    def test_entstehungszeitraum_is_oldest_document_date_to_newest_one(self):
        dossier = create(Builder('dossier'))
        create(Builder('document')
               .within(dossier)
               .with_modification_date(DateTime(2016, 1, 15))
               .with_creation_date(DateTime(2014, 3, 4)))
        create(Builder('document')
               .within(dossier)
               .with_modification_date(DateTime(2016, 3, 1))
               .with_creation_date(DateTime(2015, 1, 1)))
        create(Builder('document')
               .within(dossier)
               .with_modification_date(DateTime(2016, 12, 27))
               .with_creation_date(DateTime(2016, 1, 1)))

        binding = Dossier(dossier).binding()

        self.assertEquals(date(2014, 3, 4),
                          binding.entstehungszeitraum.von.datum.date())
        self.assertEquals(date(2016, 12, 27),
                          binding.entstehungszeitraum.bis.datum.date())

    def test_entstehungszeitraum_is_kein_angabe_when_dossier_is_empty(self):
        dossier = create(Builder('dossier'))

        binding = Dossier(dossier).binding()
        self.assertEquals(u'keine Angabe',
                          binding.entstehungszeitraum.von.datum)
        self.assertEquals(u'keine Angabe',
                          binding.entstehungszeitraum.bis.datum)

    def test_eroeffnungsdatum_is_start_date(self):
        dossier = create(Builder('dossier')
                         .having(start=date(2016, 11, 6)))

        binding = Dossier(dossier).binding()
        self.assertEquals(date(2016, 11, 6),
                          binding.eroeffnungsdatum.datum.date())

    def test_abschlussdatum_is_end_date(self):
        dossier = create(Builder('dossier')
                         .having(end=date(2016, 11, 6)))

        binding = Dossier(dossier).binding()
        self.assertEquals(date(2016, 11, 6),
                          binding.abschlussdatum.datum.date())

    def test_add_descendants_adds_all_subdossiers(self):
        dossier = create(Builder('dossier'))
        subdossier1 = create(Builder('dossier').within(dossier))
        create(Builder('dossier'))
        subdossier3 = create(Builder('dossier').within(dossier))

        model = Dossier(dossier)
        model._add_descendants()

        self.assertEquals(
            set([subdossier3, subdossier1]),
            set([mod.obj for mod in model.dossiers.values()]))

    def test_add_descendants_adds_all_containing_documents(self):
        dossier = create(Builder('dossier'))
        document1 = create(Builder('document').within(dossier))
        create(Builder('document'))
        document3 = create(Builder('document').within(dossier))

        model = Dossier(dossier)
        model._add_descendants()

        self.assertEquals(
            set([document1, document3]),
            set([doc.obj for doc in model.documents.values()]))

    @unittest.skip('Currently not implemented')
    def test_add_descendants_adds_also_documents_in_tasks(self):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))
        document = create(Builder('document').within(task))

        model = Dossier(dossier)
        model._add_descendants()

        self.assertEqual(
            set([document]),
            set([doc.obj for doc in model.documents.values()]))


class TestDocumentModel(FunctionalTestCase):

    def test_title_is_document_title_in_utf8(self):
        document = create(Builder('document')
                          .titled(u'Qualit\xe4tsumfrage'))
        self.assertEquals(u'Qualit\xe4tsumfrage',
                          Document(document).binding().titel)

    def test_autor_is_a_list_containing_document_author(self):
        document = create(Builder('document')
                          .having(document_author=u'Peter Fl\xfcckiger'))
        self.assertEquals([u'Peter Fl\xfcckiger'],
                          [author for author in Document(document).binding().autor])

    def test_erscheinungsform_is_digital_available_flag(self):
        doc_with_file = create(Builder('document').with_dummy_content())
        self.assertEquals(
            u'digital',
            Document(doc_with_file).binding().erscheinungsform)

        doc_without_file = create(Builder('document'))
        self.assertEquals(
            u'nicht digital',
            Document(doc_without_file).binding().erscheinungsform)

    def test_dokumentyp_is_document_type_title(self):
        document = create(Builder('document')
                          .having(document_type='contract'))
        self.assertEquals(
            u'Contract',
            Document(document).binding().dokumenttyp)

    def test_registrierdatum_is_created_date(self):
        document = create(Builder('document')
                          .with_creation_date(DateTime(2016, 11, 6)))

        self.assertEquals(
            date(2016, 11, 6),
            Document(document).binding().registrierdatum.datum.date())

    def test_entstehungszeitraum_is_created_to_modified_date_range(self):
        document = create(Builder('document')
                          .with_creation_date(DateTime(2016, 11, 6))
                          .with_modification_date(DateTime(2017, 12, 6)))

        entstehungszeitraum = Document(document).binding().entstehungszeitraum
        self.assertEquals(date(2016, 11, 6), entstehungszeitraum.von.datum.date())
        self.assertEquals(date(2017, 12, 6), entstehungszeitraum.bis.datum.date())


class TestFolderAndFileModel(FunctionalTestCase):

    def test_complete_tree_representation(self):
        root = create(Builder('repository_root'))
        folder = create(Builder('repository').within(root))
        dossier_a = create(Builder('dossier').within(folder))
        subdossier_a = create(Builder('dossier').within(dossier_a))
        document_a = create(Builder('document')
                            .within(subdossier_a)
                            .with_dummy_content())
        dossier_b = create(Builder('dossier').within(folder))
        document_b = create(Builder('document')
                            .within(dossier_b)
                            .with_dummy_content())

        repo = Repository()
        content = ContentRootFolder('SIP_20101212_FD_10xy')

        models = [Dossier(dossier_a), Dossier(dossier_b)]
        for dossier_model in models:
            repo.add_dossier(dossier_model)
            content.add_dossier(dossier_model)

        self.assertEquals(2, len(content.folders))
        dossier_model_a, dossier_model_b = content.folders

        # dossier a
        self.assertEquals(1, len(dossier_model_a.folders))
        subdossier_model = dossier_model_a.folders[0]
        self.assertEquals(1, len(subdossier_model.files))
        file_model_a = subdossier_model.files[0]
        self.assertEquals(u'Testdokumaent.doc', file_model_a.filename)
        self.assertEquals(document_a.file._blob.committed(), file_model_a.filepath)

        # dossier b
        self.assertEquals([], dossier_model_b.folders)
        self.assertEquals(1, len(dossier_model_b.files))
        file_model_b = dossier_model_b.files[0]
        self.assertEquals(u'Testdokumaent.doc', file_model_b.filename)
        self.assertEquals(document_b.file._blob.committed(), file_model_b.filepath)


class TestFileModel(FunctionalTestCase):

    def setUp(self):
        super(TestFileModel, self).setUp()
        self.toc = ContentRootFolder('FAKE_PATH')
        self.toc.next_file = 3239

    def test_uses_documents_archival_file_if_exist(self):
        document = create(Builder('document')
                          .attach_archival_file_containing('ARCHIVDATA', u'test.pdf')
                          .with_dummy_content())
        model = File(self.toc, Document(document))

        self.assertEquals(u'test.pdf', model.filename)
        self.assertEquals(document.archival_file._blob.committed(),
                          model.filepath)

    def test_represents_documents_file_if_no_archival_file_exist(self):
        document = create(Builder('document').with_dummy_content())
        model = File(self.toc, Document(document))

        self.assertEquals(u'Testdokumaent.doc', model.filename)
        self.assertEquals(document.file._blob.committed(), model.filepath)

    def test_named_next_file_number_prefixed_with_p(self):
        document_a = create(Builder('document').with_dummy_content())
        document_b = create(Builder('document').with_dummy_content())

        model = File(self.toc, Document(document_a))
        self.assertEquals('p003239.doc', model.name)
        model = File(self.toc, Document(document_b))
        self.assertEquals('p003240.doc', model.name)

    def test_pruefsumme_is_a_md5_hash(self):
        document = create(Builder('document')
                          .attach_archival_file_containing('Test data'))
        model = File(self.toc, Document(document))

        _hash = hashlib.md5()
        _hash.update('Test data')

        self.assertEquals(_hash.hexdigest(), model.binding().pruefsumme)
        self.assertEquals('MD5', model.binding().pruefalgorithmus)
