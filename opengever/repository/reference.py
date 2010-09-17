from Acquisition import aq_inner, aq_parent
from five import grok
from opengever.base.interfaces import IReferenceNumber
from opengever.base.reference import BasicReferenceNumber
from opengever.repository.repositoryfolder import IRepositoryFolderSchema
from opengever.repository.repositoryroot import IRepositoryRoot
from opengever.repository.behaviors.referenceprefix \
    import IReferenceNumberPrefix


class RepositoryRootNumber(BasicReferenceNumber):
    """ Reference number generator for the repository root, which just
    adds the seperator-space and is primary required because we wan't
    to traverse over it.
    """
    grok.provides(IReferenceNumber)
    grok.context(IRepositoryRoot)

    def get_number(self):
        parent_num = self.get_parent_number()
        if parent_num:
            return str(parent_num) + ' '
        return ''


class RepositoryFolderReferenceNumber(BasicReferenceNumber):
    """ Reference number for repository folder
    """
    grok.provides(IReferenceNumber)
    grok.context(IRepositoryFolderSchema)

    def get_number(self):
        # get local number prefix
        num = IReferenceNumberPrefix(self.context).reference_number_prefix
        num = num and str(num) or ''
        # get the parent number
        parent_num = self.get_parent_number()
        parent = aq_parent(aq_inner(self.context))
        if parent_num and IRepositoryFolderSchema.providedBy(parent):
            return str(parent_num) + '.' + num
        elif parent_num:
            return str(parent_num) + num
        else:
            return num
