from five import grok
from opengever.dossier.behaviors.dossier import IDossierMarker
from ftw.contentmenu.interfaces import IContentmenuPostFactoryMenu
from zope.interface import Interface
from opengever.dossier import _
from opengever.dossier.factory_utils import order_factories
from opengever.meeting import is_meeting_feature_enabled


class DossierPostFactoryMenu(grok.MultiAdapter):
    """If a task is added to another task, it is called subtask. So we need
    to change the name of the task in the add-menu if we are in a task.
    """

    grok.adapts(IDossierMarker, Interface)
    grok.implements(IContentmenuPostFactoryMenu)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_filtered(self, factory):
        factory_id = factory.get('id')
        if factory_id == u'ftw.mail.mail':
            return True
        if factory_id == u'opengever.meeting.proposal':
            return not is_meeting_feature_enabled()

        return False

    def __call__(self, factories):
        if not IDossierMarker.providedBy(self.context):
            # use default
            return factories

        filtered_factories = []
        for factory in factories:
            if factory.get('id') == u'opengever.dossier.businesscasedossier':
                factory['title'] = _(u'Subdossier')

            if not self.is_filtered(factory):
                filtered_factories.append(factory)

        return order_factories(self.context, filtered_factories)
