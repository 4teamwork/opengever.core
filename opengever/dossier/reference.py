from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.base.reference import BasicReferenceNumber
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.templatefolder import ITemplateFolder
from zope.component import adapter


@adapter(IDossierMarker)
class DossierReferenceNumber(BasicReferenceNumber):
    """ Reference number for dossier types
    """
    ref_type = 'dossier'

    def get_local_number(self):
        parent = aq_parent(aq_inner(self.context))
        prefix = IReferenceNumberPrefix(parent).get_number(self.context)

        return prefix or ''


@adapter(ITemplateFolder)
class TemplateFolderReferenceNumber(BasicReferenceNumber):
    """ Reference number for template folder.
    """

    ref_type = 'location_prefix'

    def get_local_number(self):
        return self.context.id
