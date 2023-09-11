from Acquisition import aq_inner
from Acquisition import aq_parent
from DateTime import DateTime
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.interfaces import ISequenceNumber
from opengever.base.utils import file_checksum
from opengever.disposition.ech0160 import model as ech0160
from opengever.disposition.ech0160.bindings import arelda
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from opengever.repository.repositoryroot import IRepositoryRoot
from pkg_resources import resource_filename
from plone import api
from pyxb.namespace import XMLSchema_instance as xsi
from zope.component import getUtility
import os.path


ABLIEFERUNGSTYP = u'GEVER'
SIP_PAKET_TYP = 'SIP'

schemas_path = resource_filename('opengever.disposition.ech0160', 'schemas')


class SIPPackage(object):
    """Builds a SIP package.

    See 2.4.3 Ablieferungsobjekt Paket - SIP
    http://www.ech.ch/vechweb/page?p=dossier&documentNumber=eCH-0160
    """

    def __init__(self, disposition):
        self.xsd = self.create_xsd()
        self.disposition = disposition
        self.dossiers = self.create_dossiers(
            self.disposition.get_dossiers_with_positive_appraisal())
        self.repo = self.create_repository()
        self.content_folder = self.create_content_folder()
        self.ablieferung = self.create_ablieferung()
        self.inhaltsverzeichnis = self.create_inhaltsverzeichnis()
        self.metadata = self.create_metadata()

    def create_xsd(self):
        return arelda.ordnerSIP(u'xsd', u'xsd')

    def create_dossiers(self, dossiers):
        """Returns a list of ech0160 dossier models.
        """
        return [ech0160.Dossier(dossier) for dossier in dossiers]

    def create_metadata(self):
        metadata = arelda.paketSIP(schemaVersion=u'4.1')
        metadata.paketTyp = SIP_PAKET_TYP
        metadata.inhaltsverzeichnis = self.inhaltsverzeichnis
        metadata.ablieferung = self.ablieferung
        return metadata

    def create_inhaltsverzeichnis(self):
        inhaltsverzeichnis = arelda.inhaltsverzeichnisSIP()
        header = arelda.ordnerSIP(u'header', u'header')
        header.ordner.append(self.xsd)
        inhaltsverzeichnis.ordner.append(header)
        inhaltsverzeichnis.append(self.content_folder.binding())

        return inhaltsverzeichnis

    def create_ablieferung(self):
        ablieferung = arelda.ablieferungGeverSIP()

        ablieferung.ablieferungstyp = ABLIEFERUNGSTYP
        ablieferung.ablieferndeStelle = self.get_transferring_office()
        ablieferung.provenienz = arelda.provenienzGeverSIP()
        ablieferung.provenienz.aktenbildnerName = get_current_admin_unit().label()
        ablieferung.provenienz.registratur = self.get_repository_title()

        ablieferung.ordnungssystem = self.repo.binding()

        return ablieferung

    def create_repository(self):
        repo = ech0160.Repository()
        for dossier in self.dossiers:
            repo.add_dossier(dossier)

        return repo

    def create_content_folder(self):
        content_folder = ech0160.ContentRootFolder(self.get_folder_name())
        for dossier in self.dossiers:
            content_folder.add_dossier(dossier)

        return content_folder

    def get_transferring_office(self):
        """Returns the current adminunits label, followed by the
        disposition creator's fullname.
        """
        creator = self.disposition.Creator()
        user = ogds_service().fetch_user(creator)
        fullname = user.fullname() if user else creator
        return u'{}, {}'.format(get_current_admin_unit().label(), fullname)

    def get_repository_title(self):
        # TODO: use disposition itself instead of the first dossier
        parent = self.dossiers[0].obj
        while not IRepositoryRoot.providedBy(parent):
            parent = aq_parent(aq_inner(parent))

        return ITranslatedTitle(parent).translated_title()

    def get_folder_name(self):
        seq_number = getUtility(ISequenceNumber).get_number(self.disposition)
        name = u'SIP_{}_{}_{}'.format(
            DateTime().strftime('%Y%m%d'),
            api.portal.get().getId().upper(), seq_number)
        if self.disposition.transfer_number:
            name = u'{}_{}'.format(name, self.disposition.transfer_number)

        return name

    def write_to_zipfile(self, zipfile):
        self.add_schema_files(zipfile)
        self.content_folder.add_to_zip(zipfile)
        self.add_document_files(zipfile)

    def add_schema_files(self, zipfile):
        for schema in os.listdir(schemas_path):
            filename = os.path.join(schemas_path, schema)
            arcname = os.path.join(
                self.get_folder_name(), 'header', 'xsd', schema)
            zipfile.write(filename, arcname)

            checksum_alg, checksum = file_checksum(filename)
            self.xsd.append(arelda.dateiSIP(
                schema,
                schema,
                checksum_alg,
                checksum,
                id=u'_xsd_{}'.format(os.path.splitext(schema)[0]),
            ))

    def add_document_files(self, zipfile):
        dom = self.metadata.toDOM(element_name='paket')
        dom.documentElement.setAttributeNS(
            xsi.uri(),
            u'xsi:schemaLocation',
            u'http://bar.admin.ch/arelda/v4 xsd/arelda.xsd',
        )
        dom.documentElement.setAttributeNS(
            xsi.uri(),
            u'xsi:type',
            u'paketSIP',
        )

        arcname = os.path.join(
            self.get_folder_name(), 'header', 'metadata.xml')
        zipfile.writestr(arcname, dom.toprettyxml(encoding='UTF-8'))
