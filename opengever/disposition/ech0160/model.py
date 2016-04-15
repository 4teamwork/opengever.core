from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from opengever.base.interfaces import IReferenceNumber
from opengever.disposition.ech0160.bindings import arelda
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
        parents = dossier.parents()
        if self.obj is None:
            self.obj = parents[0]
        elif self.obj != parents[0]:
            raise ValueError("Multiple repositories")
        self.add_descendants(parents[1:])

    def add_descendants(self, descendants):
        if descendants:
            obj = descendants[0]
            uid = obj.UID()
            if uid in self.positions:
                pos = self.positions[uid]
            else:
                pos = Position(obj)
                self.positions[uid] = pos
            pos.add_descendants(descendants[1:])

    def binding(self):
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

    def add_descendants(self, descendants):
        if descendants:
            obj = descendants[0]
            uid = obj.UID()
            if IRepositoryFolder.providedBy(obj):
                if uid in self.positions:
                    pos = self.positions[uid]
                else:
                    pos = Position(obj)
                    self.positions[uid] = pos
                pos.add_descendants(descendants[1:])
            elif IDossierMarker.providedBy(obj):
                if uid in self.dossiers:
                    dossier = self.dossiers[uid]
                else:
                    dossier = Dossier(obj)
                    self.dossiers[uid] = dossier

    def binding(self):
        op = arelda.ordnungssystempositionGeverSIP(
            id=u'_{}'.format(self.obj.UID()))
        op.nummer = IReferenceNumber(self.obj).get_repository_number()
        op.titel = self.obj.Title(prefix_with_reference_number=False)

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

        self.add_descendants()

    def parents(self):
        obj = self.obj
        parents = [obj]
        while True:
            obj = aq_parent(obj)
            parents.insert(0, obj)
            if obj is None or IRepositoryRoot.providedBy(obj):
                break
        return parents

    def add_descendants(self):
        objs = self.obj.objectValues()
        for obj in objs:
            if IDossierMarker.providedBy(obj):
                dossier = Dossier(obj)
                self.dossiers[obj.UID()] = dossier
                dossier.add_descendants()
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

    def binding(self):
        dokument = arelda.dokumentGeverSIP(id=u'_{}'.format(self.obj.UID()))
        dokument.titel = self.obj.Title().decode('utf8')
        if self.obj.digitally_available:
            dokument.erscheinungsform = u'digital'
        else:
            dokument.erscheinungsform = u'nicht digital'

        if self.obj.document_author:
            dokument.autor.append(self.obj.document_author)

        return dokument


class ContentRootFolder(object):
    """eCH-0160 ordnerSIP"""

    def __init__(self):
        self.next_folder = 1
        self.next_file = 1
        self.folders = []
        self.files = []

    def add_dossier(self, dossier):
        self.folders.append(Folder(self, dossier))

    def binding(self):
        ordner = arelda.ordnerSIP(u'content')
        for folder in self.folders:
            ordner.ordner.append(folder.binding())
        return ordner


class Folder(object):
    """eCH-0160 ordnerSIP"""

    def __init__(self, toc, dossier):
        self.folders = []
        self.files = []

        self.name = 'd{0:06d}'.format(toc.next_folder)
        toc.next_folder += 1

        for dossier in dossier.dossiers.values():
            self.folder.append(Folder(toc, dossier))

        for doc in dossier.documents.values():
            self.files.append(File(toc, doc))

    def binding(self):
        ordner = arelda.ordnerSIP(self.name)

        for folder in self.folders:
            ordner.ordner.append(folder.binding())

        for file_ in self.files:
            ordner.datei.append(file_.binding())

        return ordner


class File(object):

    def __init__(self, toc, document):
        self.document = document

        base, extension = os.path.splitext(document.obj.file.filename)
        self.name = 'p{0:06d}{1}'.format(toc.next_file, extension)
        toc.next_file += 1

    def binding(self):
        id_ = binascii.hexlify(self.document.obj.file._p_oid)
        datei = arelda.dateiSIP(id=u'_{}'.format(id_))
        datei.name = self.name
        datei.pruefalgorithmus = u'SHA-256'
        datei.pruefsumme = u'TODO'
        return datei
