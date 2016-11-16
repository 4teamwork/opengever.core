from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.interfaces import IReferenceNumber
from opengever.disposition.ech0160.bindings import arelda
from opengever.disposition.ech0160.model import Dossier
from opengever.disposition.ech0160.utils import set_classification_attributes
from opengever.repository.interfaces import IRepositoryFolder


class Position(object):
    """eCH-0160 ordnungssystempositionGeverSIP"""

    def __init__(self, obj):
        self.obj = obj
        self.positions = {}
        self.dossiers = {}

    def _add_descendants(self, descendants):
        if not descendants:
            return

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
        op.titel = self.obj.Title(
            prefix_with_reference_number=False).decode('utf8')

        set_classification_attributes(op, self.obj)

        op.schutzfrist = unicode(ILifeCycle(self.obj).custody_period)

        for pos in self.positions.values():
            op.ordnungssystemposition.append(pos.binding())

        for dossier in self.dossiers.values():
            op.dossier.append(dossier.binding())
        return op
