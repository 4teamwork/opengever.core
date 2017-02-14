from Acquisition import aq_parent, aq_inner
from five import grok
from opengever.base.interfaces import IReferenceNumber, IReferenceNumberPrefix
from opengever.base.reference import BasicReferenceNumber
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.templatefolder import ITemplateFolder


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


class TemplateFolderReferenceNumber(BasicReferenceNumber):
    """ Reference number for template folder.
    """
    grok.provides(IReferenceNumber)
    grok.context(ITemplateFolder)

    ref_type = 'dossier'

    def get_local_number(self):
        return self.context.title
