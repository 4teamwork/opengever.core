from opengever.disposition.ech0160.bindings import arelda
from opengever.disposition.ech0160.model import NOT_SPECIFIED
from opengever.disposition.ech0160.model import Position


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
        if not descendants:
            return

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
        os.name = self.obj.Title().decode('utf8')

        if self.obj.version:
            os.generation = self.obj.version

        if self.obj.valid_from or self.obj.valid_until:
            os.anwendungszeitraum = arelda.historischerZeitraum()
            if self.obj.valid_from:
                os.anwendungszeitraum.von = arelda.historischerZeitpunkt(
                    self.obj.valid_from)
            else:
                os.anwendungszeitraum.von = NOT_SPECIFIED
            if self.obj.valid_until:
                os.anwendungszeitraum.bis = arelda.historischerZeitpunkt(
                    self.obj.valid_until)
            else:
                os.anwendungszeitraum.bis = NOT_SPECIFIED

        for pos in self.positions.values():
            os.ordnungssystemposition.append(pos.binding())

        return os
