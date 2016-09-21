from five import grok
from opengever.base.interfaces import IReferenceNumber
from opengever.base.reference import BasicReferenceNumber
from opengever.private.folder import IPrivateFolder


class PrivateFolderReferenceNumber(BasicReferenceNumber):
    """Reference number adapter for private folder. It uses the userid
    as local number part.
    """

    grok.provides(IReferenceNumber)
    grok.context(IPrivateFolder)

    ref_type = 'repository'

    def get_local_number(self):
        return self.context.userid

    def get_repository_number(self):
        numbers = self.get_parent_numbers()
        return self.get_active_formatter().repository_number(numbers)
