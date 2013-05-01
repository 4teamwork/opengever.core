from five import grok
from opengever.inbox.inbox import IInbox
from ftw.contentmenu.interfaces import IContentmenuPostFactoryMenu
from zope.interface import Interface
from opengever.dossier.factory_utils import order_factories


class InboxPostFactoryMenu(grok.MultiAdapter):
    """Remove the mail, forwarding and yearfolder action from the factory menu.
    And use the standard ordering.
    """

    grok.adapts(IInbox, Interface)
    grok.implements(IContentmenuPostFactoryMenu)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, factories):
        if not IInbox.providedBy(self.context):
            # use default
            return factories
        cleaned_factories = []
        for factory in factories:

            if factory['extra']['id'] not in [
                u'ftw-mail-mail', u'opengever-inbox-forwarding',
                u'opengever-inbox-yearfolder']:

                cleaned_factories.append(factory)

        # Order the factory-menu
        cleaned_factories = order_factories(self.context, cleaned_factories)
        return cleaned_factories
