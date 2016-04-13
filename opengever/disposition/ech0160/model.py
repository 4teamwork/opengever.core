from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from opengever.base.interfaces import IReferenceNumber
from opengever.disposition.ech0160.bindings import arelda
from opengever.document.document import IDocumentSchema
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.repository.interfaces import IRepositoryFolder
from opengever.repository.repositoryroot import IRepositoryRoot


class Repository(object):
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

    def __init__(self, obj):
        self.obj = obj
        self.dossiers = {}
        self.documents = {}
        self.add_descendants()

    def add_descendants(self):
        catalog = getToolByName(self.obj, 'portal_catalog')
        items = catalog({'path': {'query': '/'.join(self.obj.getPhysicalPath()), 'depth': 1}})
        for item in items:
            obj = item.getObject()
            if IDossierMarker.providedBy(obj):
                dossier = Dossier(obj)
                self.dossiers[obj.UID()] = dossier
                dossier.add_descendants()
            elif IDocumentSchema.providedBy(obj):
                self.documents[obj.UID()] = Document(obj)

    def parents(self):
        obj = self.obj
        parents = [obj]
        while True:
            obj = aq_parent(obj)
            parents.insert(0, obj)
            if obj is None or IRepositoryRoot.providedBy(obj):
                break
        return parents

    def binding(self):
        dossier = arelda.dossierGeverSIP(
            id=u'_{}'.format(self.obj.UID()))
        dossier.titel = self.obj.Title().decode('utf8')

        dossier.entstehungszeitraum = arelda.historischerZeitraum()
        dossier_obj = IDossier(self.obj)
        if dossier_obj.start is None:
            dossier.entstehungszeitraum.von = u'keine Angabe'
        else:
            dossier.entstehungszeitraum.von = arelda.historischerZeitpunkt(dossier_obj.start)
        if dossier_obj.end is None:
            dossier.entstehungszeitraum.bis = u'keine Angabe'
        else:
            dossier.entstehungszeitraum.bis = arelda.historischerZeitpunkt(dossier_obj.end)

        dossier.aktenzeichen = IReferenceNumber(self.obj).get_number()

        for d in self.dossiers.values():
            dossier.dossier.append(d.binding())

        return dossier


class Document(object):

    def __init__(self, obj):
        self.obj = obj
