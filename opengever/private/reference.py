from opengever.base.reference import BasicReferenceNumber
from opengever.private.folder import IPrivateFolder
from zope.component import adapter


@adapter(IPrivateFolder)
class PrivateFolderReferenceNumber(BasicReferenceNumber):
    """Reference number adapter for private folder. It uses the userid
    as local number part.
    """
    ref_type = 'repository'

    def get_local_number(self):
        return self.context.getId()

    def get_repository_number(self):
        numbers = self.get_parent_numbers()
        return self.get_active_formatter().repository_number(numbers)
