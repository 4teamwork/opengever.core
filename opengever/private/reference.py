from opengever.base.reference import BasicReferenceNumber
from opengever.private.folder import IPrivateFolder
from opengever.private.root import IPrivateRoot
from zope.component import adapter


@adapter(IPrivateRoot)
class PrivateRootReferenceNumber(BasicReferenceNumber):
    """Reference number adapter for private roots.

    Provides a local prefix for the reference number.
    """

    ref_type = 'location_prefix'

    def get_local_number(self):
        return getattr(self.context, 'location_prefix', None)


@adapter(IPrivateFolder)
class PrivateFolderReferenceNumber(BasicReferenceNumber):
    """Reference number adapter for private folder. It uses the userid
    as local number part.
    """

    ref_type = 'repository'

    def get_local_number(self):
        return self.context.getId()

    def get_repository_number(self):
        numbers = self.get_numbers()
        return self.get_active_formatter().repository_number(numbers)
