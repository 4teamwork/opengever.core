from Acquisition import aq_parent, aq_inner
from five import grok
from opengever.base.interfaces import IReferenceNumber, IReferenceNumberPrefix
from opengever.base.reference import BasicReferenceNumber
from opengever.dossier.behaviors.dossier import IDossierMarker


class DossierReferenceNumber(BasicReferenceNumber):
    """ Reference number for dossier types
    """
    grok.provides(IReferenceNumber)
    grok.context(IDossierMarker)

    ref_type = 'dossier'

    def get_local_number(self):
        parent = aq_parent(aq_inner(self.context))
        prefix = IReferenceNumberPrefix(parent).get_number(self.context)

        return prefix or ''
