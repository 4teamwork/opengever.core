from five import grok
from opengever.base.menu import FilteredPostFactoryMenu
from opengever.inbox.inbox import IInbox
from zope.interface import Interface


class InboxPostFactoryMenu(FilteredPostFactoryMenu):
    """Remove the mail, forwarding and yearfolder action from the factory menu.
    And use the standard ordering.
    """

    grok.adapts(IInbox, Interface)

    def is_filtered(self, factory):
        return factory['extra']['id'] in [
            u'ftw-mail-mail',
            u'opengever-inbox-forwarding',
            u'opengever-inbox-yearfolder']
