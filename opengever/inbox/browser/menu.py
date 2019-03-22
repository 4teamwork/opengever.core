from opengever.base.menu import FilteredPostFactoryMenuWithWebactions
from opengever.inbox.inbox import IInbox
from zope.component import adapter
from zope.interface import Interface


@adapter(IInbox, Interface)
class InboxPostFactoryMenu(FilteredPostFactoryMenuWithWebactions):
    """Remove the mail, forwarding and yearfolder action from the factory menu.
    And use the standard ordering.
    """

    def is_filtered(self, factory):
        return factory['extra']['id'] in [
            u'ftw-mail-mail',
            u'opengever-inbox-forwarding',
            u'opengever-inbox-yearfolder']
