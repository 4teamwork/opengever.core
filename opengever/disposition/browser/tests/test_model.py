from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import staticuid
from opengever.disposition.ech0160.model import Dossier
from opengever.disposition.ech0160.model import Repository
from opengever.disposition.ech0160.model import Position
from opengever.testing import FunctionalTestCase


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
        model.add_dossier(Dossier(dossier2))

        self.assertEquals(root, model.obj)
        positions = model.positions.values()
        self.assertSequenceEqual(
            [folder1, folder2], [pos.obj for pos in positions])
        self.assertEquals([folder1_1],
                          [pos.obj for pos in positions[0].positions.values()])

    def test_name_is_root_title(self):
        root = create(Builder('repository_root').titled(u'Ordnungsystem 2001'))

        model = Repository()
        model.obj = root

        self.assertEquals(u'Ordnungsystem 2001', model.binding().name)

    def test_anwendungszeitraum_bis_is_valid_from_date_or_keine_angabe(self):
        root1 = create(Builder('repository_root')
                       .having(valid_from=date(2016, 06, 11)))
        model = Repository()
        model.obj = root1
        self.assertEquals(date(2016, 06, 11),
                          model.binding().anwendungszeitraum.von.datum.date())

        root2 = create(Builder('repository_root')
                       .having(valid_until=date(2016, 06, 11)))
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


