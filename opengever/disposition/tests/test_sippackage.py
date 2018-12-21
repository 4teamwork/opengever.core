from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.disposition.ech0160.sippackage import SIPPackage
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from tempfile import TemporaryFile
from zipfile import ZipFile


class TestSIPPackageIntegration(IntegrationTestCase):

    def test_sip_folder_name_correspond_to_ech0160_definition(self):
        """See chapter 5.4 Aufbau eines SIP in eCH-0160 definition.

        SIP_[Ablieferungsdatum]_[Name der ablieferenden Stelle]_[Referenz].
        """
        self.login(self.records_manager)
        package = SIPPackage(self.disposition)

        with freeze(datetime(2016, 11, 6)):
            self.assertEquals(
                'SIP_20161106_PLONE', package.get_folder_name())

        self.disposition.transfer_number = u'10\xe434'
        with freeze(datetime(2016, 11, 6)):
            self.assertEquals(
                u'SIP_20161106_PLONE_10\xe434', package.get_folder_name())

    def test_ablieferungs_metadata(self):
        self.login(self.records_manager)
        package = SIPPackage(self.disposition)

        self.assertEquals(
            u'GEVER', package.ablieferung.ablieferungstyp)
        self.assertEquals(
            'Hauptmandant, ramon.flucht',
            package.ablieferung.ablieferndeStelle)
        self.assertEquals(
            u'Hauptmandant', package.ablieferung.provenienz.aktenbildnerName)
        self.assertEquals(
            u'Ordnungssystem', package.ablieferung.provenienz.registratur)


class TestSIPPackage(FunctionalTestCase):

    def setUp(self):
        super(TestSIPPackage, self).setUp()
        self.root = create(Builder('repository_root')
                           .having(title_de=u'Ordnungssystem 2000'))
        self.folder = create(Builder('repository').within(self.root))
        self.grant('Contributor', 'Editor', 'Reader', 'Records Manager')

    def test_adds_all_dossiers_and_documents(self):
        dossier_a = create(Builder('dossier').within(self.folder).as_expired())
        create(Builder('document').with_dummy_content().within(dossier_a))
        dossier_b = create(Builder('dossier').within(self.folder).as_expired())
        dossier_c = create(Builder('dossier').within(self.folder).as_expired())
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
        self.assertEquals(1, len(dossier_a_model.files))
        self.assertEquals(0, len(dossier_b_model.files))

    def test_handles_documents_without_a_file_correctly(self):
        dossier_a = create(Builder('dossier').within(self.folder).as_expired())
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
        dossier_a = create(Builder('dossier').within(self.folder).as_expired())
        dossier_b = create(Builder('dossier').within(self.folder).as_expired())
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
                ['SIP_20160611_PLONE_10xy/header/xsd/ablieferung.xsd',
                 'SIP_20160611_PLONE_10xy/header/xsd/archivischeNotiz.xsd',
                 'SIP_20160611_PLONE_10xy/header/xsd/archivischerVorgang.xsd',
                 'SIP_20160611_PLONE_10xy/header/xsd/arelda.xsd',
                 'SIP_20160611_PLONE_10xy/header/xsd/base.xsd',
                 'SIP_20160611_PLONE_10xy/header/xsd/datei.xsd',
                 'SIP_20160611_PLONE_10xy/header/xsd/dokument.xsd',
                 'SIP_20160611_PLONE_10xy/header/xsd/dossier.xsd',
                 'SIP_20160611_PLONE_10xy/header/xsd/ordner.xsd',
                 'SIP_20160611_PLONE_10xy/header/xsd/ordnungssystem.xsd',
                 'SIP_20160611_PLONE_10xy/header/xsd/ordnungssystemposition.xsd',
                 'SIP_20160611_PLONE_10xy/header/xsd/paket.xsd',
                 'SIP_20160611_PLONE_10xy/header/xsd/provenienz.xsd',
                 'SIP_20160611_PLONE_10xy/header/xsd/zusatzDaten.xsd',
                 'SIP_20160611_PLONE_10xy/content/d000001/p000001.doc',
                 'SIP_20160611_PLONE_10xy/content/d000002/p000002.pdf',
                 'SIP_20160611_PLONE_10xy/header/metadata.xml'],
                zip_file.namelist())
