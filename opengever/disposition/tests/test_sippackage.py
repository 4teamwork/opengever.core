from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.disposition.ech0160.sippackage import SIPPackage
from opengever.disposition.interfaces import IAppraisal
from opengever.disposition.interfaces import IDispositionSettings
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone import api
from tempfile import TemporaryFile
from zipfile import ZipFile
import csv


class TestSIPPackageIntegration(IntegrationTestCase):

    def test_sip_folder_name_correspond_to_ech0160_definition(self):
        """See chapter 5.4 Aufbau eines SIP in eCH-0160 definition.

        SIP_[Ablieferungsdatum]_[Name der ablieferenden Stelle]_[Referenz].
        """
        self.login(self.records_manager)
        package = SIPPackage(self.disposition)

        with freeze(datetime(2016, 11, 6)):
            self.assertEquals(
                'SIP_20161106_PLONE_1', package.get_folder_name())

        self.disposition.transfer_number = u'10\xe434'
        with freeze(datetime(2016, 11, 6)):
            self.assertEquals(
                u'SIP_20161106_PLONE_1_10\xe434', package.get_folder_name())

    def test_ablieferungs_metadata(self):
        rm_user = ogds_service().fetch_user(self.records_manager.getId())
        rm_user.firstname = u'R\xe4mon'
        get_current_admin_unit().title = u'Hauptmand\xe4nt'

        self.login(self.records_manager)
        package = SIPPackage(self.disposition)

        self.assertEquals(
            u'GEVER', package.ablieferung.ablieferungstyp)
        self.assertEquals(
            u'Hauptmand\xe4nt, Flucht R\xe4mon',
            package.ablieferung.ablieferndeStelle)
        self.assertEquals(
            u'Ordnungssystem', package.ablieferung.provenienz.registratur)
        # aktenbildnerName default is admin unit label, but it was set
        # before the change done above
        self.assertEquals(
            u'Hauptmandant', package.ablieferung.provenienz.aktenbildnerName)

        # Can overwrite aktenbildnerName
        self.disposition.transferring_office = "my custom transferring office"
        package = SIPPackage(self.disposition)
        self.assertEquals(
            u'my custom transferring office', package.ablieferung.provenienz.aktenbildnerName)


class TestSIPPackage(FunctionalTestCase):

    def setUp(self):
        super(TestSIPPackage, self).setUp()
        self.root = create(Builder('repository_root')
                           .having(title_de=u'Ordnungssystem 2000'))
        self.folder = create(Builder('repository').within(self.root))
        self.grant('Contributor', 'Editor', 'Reader', 'Records Manager')

    def test_adds_all_dossiers_documents_and_mails(self):
        dossier_a = create(Builder('dossier')
                           .within(self.folder)
                           .as_expired()
                           .having(archival_value=ARCHIVAL_VALUE_WORTHY))
        create(Builder('document').with_dummy_content().within(dossier_a))
        create(Builder('mail').with_dummy_message().within(dossier_a))
        dossier_b = create(Builder('dossier')
                           .within(self.folder)
                           .as_expired()
                           .having(archival_value=ARCHIVAL_VALUE_WORTHY))
        create(Builder('dossier')
               .within(self.folder)
               .as_expired()
               .having(archival_value=ARCHIVAL_VALUE_WORTHY))
        disposition = create(Builder('disposition')
                             .having(dossiers=[dossier_a, dossier_b])
                             .within(self.folder))

        package = SIPPackage(disposition)

        # test that dossier_c is not in package
        self.assertEquals(2, len(package.dossiers))
        self.assertItemsEqual([dossier_a, dossier_b],
                              [dossier.obj for dossier in package.dossiers])
        self.assertEquals(2, len(package.content_folder.folders))

        dossier_a_model, dossier_b_model = package.content_folder.folders
        self.assertEquals(2, len(dossier_a_model.files))
        self.assertEquals(0, len(dossier_b_model.files))

    def test_adds_only_dossiers_with_positive_appraisal(self):
        dossier_a = create(Builder('dossier')
                           .within(self.folder)
                           .as_expired()
                           .having(archival_value=ARCHIVAL_VALUE_WORTHY))
        dossier_b = create(Builder('dossier')
                           .within(self.folder)
                           .as_expired()
                           .having(archival_value=ARCHIVAL_VALUE_WORTHY))
        disposition = create(Builder('disposition')
                             .having(dossiers=[dossier_a, dossier_b])
                             .within(self.folder))

        package = SIPPackage(disposition)

        # test both dossiers are included
        self.assertEquals(2, len(package.dossiers))
        self.assertItemsEqual([dossier_a, dossier_b],
                              [dossier.obj for dossier in package.dossiers])
        self.assertEquals(2, len(package.content_folder.folders))

        IAppraisal(disposition).update(dossier=dossier_a, archive=False)

        package = SIPPackage(disposition)

        # test only archival worthy dossier is included
        self.assertEquals(1, len(package.dossiers))
        self.assertItemsEqual([dossier_b],
                              [dossier.obj for dossier in package.dossiers])
        self.assertEquals(1, len(package.content_folder.folders))

    def test_handles_documents_without_a_file_correctly(self):
        dossier_a = create(Builder('dossier')
                           .within(self.folder)
                           .as_expired()
                           .having(archival_value=ARCHIVAL_VALUE_WORTHY))
        create(Builder('document').with_dummy_content().within(dossier_a))
        create(Builder('document').within(dossier_a))
        disposition = create(Builder('disposition')
                             .having(dossiers=[dossier_a])
                             .within(self.folder))

        package = SIPPackage(disposition)

        dossier_a_model = package.content_folder.folders[0]
        self.assertEquals(1, len(dossier_a_model.files))
        self.assertEquals(2, len(package.dossiers[0].documents))

    def test_zipfile_structure(self):
        dossier_a = create(Builder('dossier')
                           .within(self.folder)
                           .as_expired()
                           .having(archival_value=ARCHIVAL_VALUE_WORTHY))
        dossier_b = create(Builder('dossier')
                           .within(self.folder)
                           .as_expired()
                           .having(archival_value=ARCHIVAL_VALUE_WORTHY))
        create(Builder('document').with_dummy_content().within(dossier_a))
        create(Builder('document')
               .with_dummy_content()
               .attach_archival_file_containing('TEST DATA')
               .within(dossier_b))
        disposition = create(Builder('disposition')
                             .having(dossiers=[dossier_a, dossier_b],
                                     transfer_number=u'10xy')
                             .within(self.folder))

        with freeze(datetime(2016, 6, 11)):
            tmpfile = TemporaryFile()
            zip_file = ZipFile(tmpfile, 'w')

            package = SIPPackage(disposition)
            package.write_to_zipfile(zip_file)
            self.assertItemsEqual(
                ['SIP_20160611_PLONE_1_10xy/header/xsd/ablieferung.xsd',
                 'SIP_20160611_PLONE_1_10xy/header/xsd/archivischeNotiz.xsd',
                 'SIP_20160611_PLONE_1_10xy/header/xsd/archivischerVorgang.xsd',
                 'SIP_20160611_PLONE_1_10xy/header/xsd/arelda.xsd',
                 'SIP_20160611_PLONE_1_10xy/header/xsd/base.xsd',
                 'SIP_20160611_PLONE_1_10xy/header/xsd/datei.xsd',
                 'SIP_20160611_PLONE_1_10xy/header/xsd/dokument.xsd',
                 'SIP_20160611_PLONE_1_10xy/header/xsd/dossier.xsd',
                 'SIP_20160611_PLONE_1_10xy/header/xsd/ordner.xsd',
                 'SIP_20160611_PLONE_1_10xy/header/xsd/ordnungssystem.xsd',
                 'SIP_20160611_PLONE_1_10xy/header/xsd/ordnungssystemposition.xsd',
                 'SIP_20160611_PLONE_1_10xy/header/xsd/paket.xsd',
                 'SIP_20160611_PLONE_1_10xy/header/xsd/provenienz.xsd',
                 'SIP_20160611_PLONE_1_10xy/header/xsd/zusatzDaten.xsd',
                 'SIP_20160611_PLONE_1_10xy/content/d000001/p000001.doc',
                 'SIP_20160611_PLONE_1_10xy/content/d000002/p000002.pdf',
                 'SIP_20160611_PLONE_1_10xy/content/d000002/p000003.doc',
                 'SIP_20160611_PLONE_1_10xy/header/metadata.xml'],
                zip_file.namelist())

    def test_adds_dossiers_csv(self):
        api.portal.set_registry_record(
            name='attach_csv_reports', interface=IDispositionSettings,
            value=True)

        with freeze(datetime(2016, 6, 11)):
            dossier_a = create(Builder('dossier')
                               .within(self.folder)
                               .as_expired()
                               .having(archival_value=ARCHIVAL_VALUE_WORTHY,
                                       description=u'Lorem ipsum'))
            dossier_b = create(Builder('dossier')
                               .within(self.folder)
                               .as_expired()
                               .having(archival_value=ARCHIVAL_VALUE_WORTHY))
            disposition = create(Builder('disposition')
                                 .having(dossiers=[dossier_a, dossier_b])
                                 .within(self.folder))

            tmpfile = TemporaryFile()
            zip_file = ZipFile(tmpfile, 'w')

            package = SIPPackage(disposition)
            package.write_to_zipfile(zip_file)
            rows = csv.DictReader(
                zip_file.read(u'SIP_20160611_PLONE_1/dossiers.csv').splitlines(),
                delimiter=';')
            rows = [row for row in rows]

            self.assertDictContainsSubset(
                {'Ablage_Nr': '',
                 'Ablage_Pr\xe4fix': '',
                 'Beschreibung': 'Lorem ipsum',
                 'Dossier_Titel': '',
                 'Mandant': 'Admin Unit 1',
                 'Ordnungssystem_Pfad': 'Ordnungssystem 2000/1. None',
                 'Ordnungsystem_Version': '',
                 'abschlussdatum': '2000-00-11',
                 'aktenzeichen': 'Client1 1 / 1',
                 'datenschutz': 'false',
                 'entstehungszeitraum_bis': '',
                 'entstehungszeitraum_von': '',
                 'eroeffnungsdatum': '2016-00-11',
                 'klassifizierungskategorie': 'unprotected',
                 'oeffentlichkeitsstatus': 'unchecked',
                 'schutzfrist': '30'},
                rows[0]
            )

            self.assertDictContainsSubset(
                {'Ablage_Nr': '',
                 'Ablage_Pr\xe4fix': '',
                 'Beschreibung': '',
                 'Dossier_Titel': '',
                 'Mandant': 'Admin Unit 1',
                 'Ordnungssystem_Pfad': 'Ordnungssystem 2000/1. None',
                 'Ordnungsystem_Version': '',
                 'abschlussdatum': '2000-00-11',
                 'aktenzeichen': 'Client1 1 / 2',
                 'datenschutz': 'false',
                 'entstehungszeitraum_bis': '',
                 'entstehungszeitraum_von': '',
                 'eroeffnungsdatum': '2016-00-11',
                 'klassifizierungskategorie': 'unprotected',
                 'oeffentlichkeitsstatus': 'unchecked',
                 'schutzfrist': '30'},
                rows[1]
            )

    def test_adds_items_csv(self):
        api.portal.set_registry_record(
            name='attach_csv_reports', interface=IDispositionSettings,
            value=True)

        with freeze(datetime(2016, 6, 11)):
            dossier_a = create(Builder('dossier')
                               .within(self.folder)
                               .as_expired()
                               .having(archival_value=ARCHIVAL_VALUE_WORTHY,
                                       description=u'Lorem ipsum'))
            create(Builder('document')
                   .with_dummy_content()
                   .attach_archival_file_containing('ARCHIV')
                   .within(dossier_a))
            disposition = create(Builder('disposition')
                                 .having(dossiers=[dossier_a, ])
                                 .within(self.folder))

            tmpfile = TemporaryFile()
            zip_file = ZipFile(tmpfile, 'w')

            package = SIPPackage(disposition)
            package.write_to_zipfile(zip_file)
            rows = csv.DictReader(
                zip_file.read(u'SIP_20160611_PLONE_1/items.csv').splitlines(),
                delimiter=';')
            rows = [row for row in rows]

            self.assertDictContainsSubset(
                {'aktenzeichen': 'Client1 1 / 1 / 1',
                 'autor': '',
                 'beschreibung': '',
                 'datenschutz': 'false',
                 'document_title': 'Testdokum\xc3\xa4nt',
                 'dokumentdatum': '2016-00-11',
                 'entstehtungszeitraum_bis': '2016-00-11',
                 'entstehtungszeitraum_von': '2016-00-11',
                 'erscheinungsform': 'digital',
                 'klassifizierungskategorie': 'unprotected',
                 'laufnummer': '1',
                 'oeffentlichkeitsstatus': 'unchecked',
                 'oeffentlichkeitsstatusBegruendung': '',
                 'originalName': 'test.pdf',
                 'pruefalgorithmus': 'MD5',
                 'pruefsumme': 'c37c17466ea0547efb1744bb061737a1',
                 'registrierdatum': '2016-00-11',
                 'sip_file_name': 'p000001.pdf',
                 'sip_folder_name': 'd000001'},
                rows[0]
            )

            self.assertDictContainsSubset(
                {'aktenzeichen': 'Client1 1 / 1 / 1',
                 'autor': '',
                 'beschreibung': '',
                 'datenschutz': 'false',
                 'document_title': 'Testdokum\xc3\xa4nt',
                 'dokumentdatum': '2016-00-11',
                 'entstehtungszeitraum_bis': '2016-00-11',
                 'entstehtungszeitraum_von': '2016-00-11',
                 'erscheinungsform': 'digital',
                 'klassifizierungskategorie': 'unprotected',
                 'laufnummer': '1',
                 'oeffentlichkeitsstatus': 'unchecked',
                 'oeffentlichkeitsstatusBegruendung': '',
                 'originalName': 'Testdokumaent.doc',
                 'pruefalgorithmus': 'MD5',
                 'pruefsumme': 'ca1ea02c10b7c37f425b9b7dd86d5e11',
                 'registrierdatum': '2016-00-11',
                 'sip_file_name': 'p000002.doc',
                 'sip_folder_name': 'd000001'},
                rows[1]
            )
