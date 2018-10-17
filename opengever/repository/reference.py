from opengever.base.reference import BasicReferenceNumber
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix
from opengever.repository.repositoryfolder import IRepositoryFolderSchema
from opengever.repository.repositoryroot import IRepositoryRoot
from zope.component import adapter


@adapter(IRepositoryRoot)
class RepositoryRootNumber(BasicReferenceNumber):
    """ Reference number generator for the repository root, which just
    adds the seperator-space and is primary required because we wan't
    to traverse over it.
    """
    ref_type = 'repositoryroot'

    def get_number(self):
        parent_num = self.get_parent_numbers()
        if parent_num:
            return str(parent_num) + ' '
        return ''


@adapter(IRepositoryFolderSchema)
class RepositoryFolderReferenceNumber(BasicReferenceNumber):
    """ Reference number for repository folder
    """
    ref_type = 'repository'

    def get_local_number(self):
        prefix = IReferenceNumberPrefix(self.context).reference_number_prefix

        return prefix or ''

    def get_repository_number(self):
        numbers = self.get_parent_numbers()

        return self.get_active_formatter().repository_number(numbers)
