from opengever.base.reference import BasicReferenceNumber
from opengever.inbox.inbox import IInbox
from zope.component import adapter


@adapter(IInbox)
class InboxReferenceNumber(BasicReferenceNumber):
    """ Reference number for inboxes.
    """

    ref_type = 'location_prefix'

    def get_local_number(self):
        return self.context.id
