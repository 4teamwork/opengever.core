from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.disposition.ech0160.sippackage import SIPPackage
from opengever.testing import FunctionalTestCase
from tempfile import TemporaryFile
from zipfile import ZipFile


class TestSIPPackage(FunctionalTestCase):

    def setUp(self):
        super(TestSIPPackage, self).setUp()
        self.root = create(Builder('repository_root')
                           .having(title_de=u'Ordnungssytem 2000'))
        self.folder = create(Builder('repository').within(self.root))

    def test_sip_folder_name_correspond_to_ech0160_definition(self):
        """See chapter 5.4 Aufbau eines SIP in eCH-0160 definition.

        SIP_[Ablieferungsdatum]_[Name der ablieferenden Stelle]_[Referenz].
        """
        dossier = create(Builder('dossier').within(self.folder))

        with freeze(datetime(2016, 11, 6)):
            package = SIPPackage([dossier])
            self.assertEquals(
                'SIP_20161106_PLONE_MyRef', package.get_folder_name())

    def test_ablieferungs_metadata(self):
        dossier = create(Builder('dossier').within(self.folder))

        package = SIPPackage([dossier])

        self.assertEquals(
            u'GEVER', package.ablieferung.ablieferungstyp)
        self.assertEquals(
            'Client1, test_user_1_',
            package.ablieferung.ablieferndeStelle)
        self.assertEquals(
            u'Client1', package.ablieferung.provenienz.aktenbildnerName)
        self.assertEquals(
            u'Ordnungssytem 2000', package.ablieferung.provenienz.registratur)

    # TODO: should only include all dossiers from the disposition object
    def test_adds_all_dossiers_and_documents(self):
        dossier_a = create(Builder('dossier').within(self.folder))
        create(Builder('document').with_dummy_content().within(dossier_a))
        dossier_b = create(Builder('dossier').within(self.folder))

        package = SIPPackage([dossier_a, dossier_b])

        dossier_a_model, dossier_b_model = package.content_folder.folders
        self.assertEquals(1, len(dossier_a_model.files))
        self.assertEquals(0, len(dossier_b_model.files))

    def test_zipfile_structure(self):
        dossier_a = create(Builder('dossier').within(self.folder))
        dossier_b = create(Builder('dossier').within(self.folder))
        create(Builder('document').with_dummy_content().within(dossier_a))
        create(Builder('document')
               .with_dummy_content()
               .attach_archival_file_containing('TEST DATA')
               .within(dossier_b))

        with freeze(datetime(2016, 6, 11)):
            tmpfile = TemporaryFile()
            zip_file = ZipFile(tmpfile, 'w')

            package = SIPPackage([dossier_a, dossier_b])
            package.write_to_zipfile(zip_file)

            self.assertItemsEqual(
                ['SIP_20160611_PLONE_MyRef/header/xsd/ablieferung.xsd',
                 'SIP_20160611_PLONE_MyRef/header/xsd/archivischeNotiz.xsd',
                 'SIP_20160611_PLONE_MyRef/header/xsd/archivischerVorgang.xsd',
                 'SIP_20160611_PLONE_MyRef/header/xsd/arelda.xsd',
                 'SIP_20160611_PLONE_MyRef/header/xsd/base.xsd',
                 'SIP_20160611_PLONE_MyRef/header/xsd/datei.xsd',
                 'SIP_20160611_PLONE_MyRef/header/xsd/dokument.xsd',
                 'SIP_20160611_PLONE_MyRef/header/xsd/dossier.xsd',
                 'SIP_20160611_PLONE_MyRef/header/xsd/ordner.xsd',
                 'SIP_20160611_PLONE_MyRef/header/xsd/ordnungssystem.xsd',
                 'SIP_20160611_PLONE_MyRef/header/xsd/ordnungssystemposition.xsd',
                 'SIP_20160611_PLONE_MyRef/header/xsd/paket.xsd',
                 'SIP_20160611_PLONE_MyRef/header/xsd/provenienz.xsd',
                 'SIP_20160611_PLONE_MyRef/header/xsd/zusatzDaten.xsd',
                 'SIP_20160611_PLONE_MyRef/content/d000001/p000001.doc',
                 'SIP_20160611_PLONE_MyRef/content/d000002/p000002.pdf',
                 'SIP_20160611_PLONE_MyRef/header/metadata.xml'],
                zip_file.namelist())
