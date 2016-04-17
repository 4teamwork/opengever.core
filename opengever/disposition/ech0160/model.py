from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from opengever.base.behaviors.classification import IClassification
from opengever.base.interfaces import IReferenceNumber
from opengever.disposition.ech0160.bindings import arelda
from opengever.disposition.ech0160.utils import file_checksum
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.document import IDocumentSchema
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.repository.interfaces import IRepositoryFolder
from opengever.repository.repositoryroot import IRepositoryRoot

import binascii
import os.path


class Repository(object):
    """eCH-0160 ordnungssystemGeverSIP"""

    def __init__(self):
        self.obj = None
        self.positions = {}

    def add_dossier(self, dossier):
        """Add a dossier to the model"""
        parents = dossier.parents()
        if self.obj is None:
            self.obj = parents[0]
        elif self.obj != parents[0]:
            raise ValueError("Multiple repositories")
        self._add_descendants(parents[1:])

    def _add_descendants(self, descendants):
        if descendants:
            obj = descendants[0]
            uid = obj.UID()
            if uid in self.positions:
                pos = self.positions[uid]
            else:
                pos = Position(obj)
                self.positions[uid] = pos
            pos._add_descendants(descendants[1:])

    def binding(self):
        """Return XML binding"""
        os = arelda.ordnungssystemGeverSIP()
        os.name = self.obj.Title()
        for pos in self.positions.values():
            os.ordnungssystemposition.append(pos.binding())
        return os


class Position(object):
    """eCH-0160 ordnungssystempositionGeverSIP"""

    def __init__(self, obj):
        self.obj = obj
        self.positions = {}
        self.dossiers = {}

    def _add_descendants(self, descendants):
        if descendants:
            obj = descendants[0]
            if IRepositoryFolder.providedBy(obj):
                uid = obj.UID()
                if uid in self.positions:
                    pos = self.positions[uid]
                else:
                    pos = Position(obj)
                    self.positions[uid] = pos
                pos._add_descendants(descendants[1:])
            elif isinstance(obj, Dossier):
                uid = obj.obj.UID()
                if uid in self.dossiers:
                    dossier = self.dossiers[uid]
                else:
                    dossier = obj
                    self.dossiers[uid] = dossier

    def binding(self):
        op = arelda.ordnungssystempositionGeverSIP(
            id=u'_{}'.format(self.obj.UID()))
        op.nummer = IReferenceNumber(self.obj).get_repository_number()
        op.titel = self.obj.Title(prefix_with_reference_number=False).decode('utf8')

        for pos in self.positions.values():
            op.ordnungssystemposition.append(pos.binding())

        for dossier in self.dossiers.values():
            op.dossier.append(dossier.binding())
        return op


class Dossier(object):
    """eCH-0160 dossierGeverSIP"""

    document_types = ['opengever.document.document']

    def __init__(self, obj):
        self.obj = obj
        self.dossiers = {}
        self.documents = {}

        self._add_descendants()

    def parents(self):
        obj = self.obj
        parents = [self]
        while True:
            obj = aq_parent(obj)
            parents.insert(0, obj)
            if obj is None or IRepositoryRoot.providedBy(obj):
                break
        return parents

    def _add_descendants(self):
        objs = self.obj.objectValues()
        for obj in objs:
            if IDossierMarker.providedBy(obj):
                self.dossiers[obj.UID()] = Dossier(obj)
            elif IDocumentSchema.providedBy(obj):
                self.documents[obj.UID()] = Document(obj)

    def binding(self):
        dossier = arelda.dossierGeverSIP(id=u'_{}'.format(self.obj.UID()))
        dossier.titel = self.obj.Title().decode('utf8')

        dossier.entstehungszeitraum = arelda.historischerZeitraum()

        catalog = getToolByName(self.obj, 'portal_catalog')
        oldest_docs = catalog(
            portal_type=self.document_types,
            path='/'.join(self.obj.getPhysicalPath()),
            sort_on='created',
            sort_order='ascending',
            sort_limit=1)
        if oldest_docs:
            dossier.entstehungszeitraum.von = arelda.historischerZeitpunkt(
                oldest_docs[0].created.asdatetime().date())
        else:
            dossier.entstehungszeitraum.von = u'keine Angabe'
        latest_docs = catalog(
            portal_type=self.document_types,
            path='/'.join(self.obj.getPhysicalPath()),
            sort_on='modified',
            sort_order='descending',
            sort_limit=1)
        if oldest_docs:
            dossier.entstehungszeitraum.bis = arelda.historischerZeitpunkt(
                latest_docs[0].modified.asdatetime().date())
        else:
            dossier.entstehungszeitraum.bis = u'keine Angabe'

        dossier.aktenzeichen = IReferenceNumber(self.obj).get_number()

        dossier_obj = IDossier(self.obj)
        if dossier_obj.start:
            dossier.eroeffnungsdatum = arelda.historischerZeitpunkt(
                dossier_obj.start)
        if dossier_obj.end:
            dossier.abschlussdatum = arelda.historischerZeitpunkt(
                dossier_obj.end)

        for d in self.dossiers.values():
            dossier.dossier.append(d.binding())

        for doc in self.documents.values():
            dossier.dokument.append(doc.binding())

        return dossier


class Document(object):
    """eCH-0160 dokumentGeverSIP"""

    def __init__(self, obj):
        self.obj = obj
        self.file_ref = None

    def binding(self):
        dokument = arelda.dokumentGeverSIP(id=u'_{}'.format(self.obj.UID()))
        dokument.titel = self.obj.Title().decode('utf8')
        if self.file_ref:
            dokument.dateiRef.append(self.file_ref)

        if self.obj.digitally_available:
            dokument.erscheinungsform = u'digital'
        else:
            dokument.erscheinungsform = u'nicht digital'

        md = IDocumentMetadata(self.obj)
        if md.document_author:
            dokument.autor.append(md.document_author)

        dokument.dokumenttyp = md.document_type

        dokument.registrierdatum = arelda.historischerZeitpunkt(
            self.obj.created().asdatetime().date())

        classification = IClassification(self.obj)
        dokument.klassifizierungskategorie = classification.classification
        dokument.datenschutz = True if classification.privacy_layer == 'privacy_layer_yes' else False
        dokument.oeffentlichkeitsstatus = classification.public_trial
        dokument.oeffentlichkeitsstatusBegruendung = classification.public_trial_statement
        return dokument


class Folder(object):
    """eCH-0160 ordnerSIP"""

    def __init__(self, toc, dossier, base_path):
        self.folders = []
        self.files = []

        self.name = u'd{0:06d}'.format(toc.next_folder)
        toc.next_folder += 1
        self.path = os.path.join(base_path, self.name)

        for dossier in dossier.dossiers.values():
            self.folder.append(Folder(toc, dossier, self.path))

        for doc in dossier.documents.values():
            self.files.append(File(toc, doc))

    def binding(self):
        ordner = arelda.ordnerSIP(self.name)

        for folder in self.folders:
            ordner.ordner.append(folder.binding())

        for file_ in self.files:
            ordner.datei.append(file_.binding())

        return ordner

    def add_to_zip(self, zipfile):
        for file_ in self.files:
            zipfile.write(file_.filepath, os.path.join(self.path, file_.name))
        for folder in self.folders:
            folder.add_to_zip(zipfile)


class ContentRootFolder(Folder):
    """eCH-0160 content root folder of type ordnerSIP"""

    def __init__(self, base_path):
        self.next_folder = 1
        self.next_file = 1
        self.name = u'content'
        self.path = os.path.join(base_path, self.name)
        self.folders = []
        self.files = []

    def add_dossier(self, dossier):
        self.folders.append(Folder(self, dossier, self.path))


class File(object):
    """eCH-0160 dateiSIP"""

    def __init__(self, toc, document):
        self.file = document.obj.archival_file or document.obj.file
        self.id = u'_{}'.format(binascii.hexlify(self.file._p_oid))
        document.file_ref = self.id
        self.document = document
        self.filename = self.file.filename
        self.filepath = self.file._blob.committed()

        base, extension = os.path.splitext(self.filename)
        self.name = 'p{0:06d}{1}'.format(toc.next_file, extension)
        toc.next_file += 1

    def binding(self):
        datei = arelda.dateiSIP(id=self.id)
        datei.name = self.name
        datei.originalName = self.filename
        datei.pruefalgorithmus = u'MD5'
        datei.pruefsumme = file_checksum(self.filepath)
        return datei
