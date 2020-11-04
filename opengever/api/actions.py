from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.webactions.interfaces import IWebActionsProvider
from opengever.webactions.renderer import WebActionsSafeDataGetter
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services.actions.get import Actions
from plone.restapi.services.actions.get import ActionsGet
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


WEBACTION_ATTRIBUTE_WHITELIST = [
    'action_id',
    'title',
    'target_url',
    'display',
    'mode',
]


@implementer(IExpandableElement)
@adapter(Interface, IOpengeverBaseLayer)
class GeverActions(Actions):

    def __call__(self, expand=False):
        actions = super(GeverActions, self).__call__(expand=expand)

        if not expand:
            return actions

        self.extend_with_webactions(actions.get('actions'))

        return actions

    def extend_with_webactions(self, actions):
        """Extends the plone actions with a new category called `webactions`.

        This category includes all available webactions for the current
        environment (context, user, permissions, webaction-settings) in a flat
        structure.
        """
        data_getter = WebActionsSafeDataGetter(self.context, self.request, None)
        webactions = [
            {key: webaction.get(key) for key in WEBACTION_ATTRIBUTE_WHITELIST}
            for webaction in data_getter.get_webactions_data(flat=True)]

        if webactions:
            actions['webactions'] = json_compatible(webactions)


class GeverActionsGet(ActionsGet):
    def reply(self):
        actions = GeverActions(self.context, self.request)
        return actions(expand=True)["actions"]
