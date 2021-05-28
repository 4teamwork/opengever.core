from opengever.base.reference import BasicReferenceNumber
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix
from opengever.repository.repositoryfolder import IRepositoryFolderSchema
from opengever.repository.repositoryroot import IRepositoryRoot
from zope.component import adapter


@adapter(IRepositoryRoot)
class RepositoryRootNumber(BasicReferenceNumber):
    """ Reference number generator for the repository root
    """
    ref_type = 'repositoryroot'

    def get_local_number(self):
        return self.context.reference_number_addendum or ''


@adapter(IRepositoryFolderSchema)
class RepositoryFolderReferenceNumber(BasicReferenceNumber):
    """ Reference number for repository folder
    """
    ref_type = 'repository'

    def get_local_number(self):
        prefix = IReferenceNumberPrefix(self.context).reference_number_prefix

        return prefix or ''

    def get_repository_number(self):
        numbers = self.get_numbers()

        return self.get_active_formatter().repository_number(numbers)
