from five import grok
from ftw.contentmenu.interfaces import IContentmenuPostFactoryMenu
from opengever.meeting import is_meeting_feature_enabled
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.interface import Interface


class PloneSitePostFactoryMenu(grok.MultiAdapter):
    """If a task is added to another task, it is called subtask. So we need
    to change the name of the task in the add-menu if we are in a task.
    """

    grok.adapts(IPloneSiteRoot, Interface)
    grok.implements(IContentmenuPostFactoryMenu)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_filtered(self, factory):
        factory_id = factory.get('id')
        if factory_id == u'opengever.meeting.committeecontainer':
            return not is_meeting_feature_enabled()

        return False

    def __call__(self, factories):
        filtered_factories = []
        for factory in factories:
            if not self.is_filtered(factory):
                filtered_factories.append(factory)

        return filtered_factories
