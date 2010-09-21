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

    def get_number(self):
        # get local number prefix
        num = IReferenceNumberPrefix(
            aq_parent(aq_inner(self.context))).get_number(self.context)
        num = num and str(num) or ''
        # get the parent number
        parent_num = self.get_parent_number()
        parent = aq_parent(aq_inner(self.context))
        if parent_num and IDossierMarker.providedBy(parent):
            return str(parent_num) + '.' + num
        elif parent_num:
            return str(parent_num) + ' / ' + num
        else:
            return num
