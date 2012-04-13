from five import grok
from opengever.dossier.behaviors.dossier import IDossierMarker
from ftw.contentmenu.interfaces import IContentmenuPostFactoryMenu
from zope.interface import Interface
from opengever.dossier import _
from opengever.dossier.factory_utils import order_factories


class DossierPostFactoryMenu(grok.MultiAdapter):
    """If a task is added to another task, it is called subtask. So we need
    to change the name of the task in the add-menu if we are in a task.
    """

    grok.adapts(IDossierMarker, Interface)
    grok.implements(IContentmenuPostFactoryMenu)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, factories):
        if not IDossierMarker.providedBy(self.context):
            # use default
            return factories
        for factory in factories:
            if factory['extra']['id'] == u'opengever-dossier-businesscasedossier':
                factory['title'] = _(u'Subdossier')
            elif factory['extra']['id'] == u'ftw-mail-mail':
                factories.remove(factory)

        # Order the factory-menu
        factories = order_factories(self.context, factories)
        return factories
