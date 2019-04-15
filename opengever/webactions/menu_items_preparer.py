from opengever.webactions.interfaces import IWebActionsMenuItemsPreparer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from opengever.webactions.renderer import WebActionsSafeDataGetter


@implementer(IWebActionsMenuItemsPreparer)
@adapter(Interface, IBrowserRequest)
class BaseWebActionsMenuItemsPreparer(object):
    """Base BaseWebActionsMenuItemsPreparer implementation serving as baseclass
    for preparers specific to a given display location.
    Attributes/methods that have to be overwritten in a subclass:
        - display: the display location of the webactions.
        - prepare_webaction: method called on each webaction used to prepare
                             the data as needed for a given display location
    """

    display = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        data_getter = WebActionsSafeDataGetter(self.context, self.request,
                                               self.display)

        webactions = data_getter.get_webactions_data().get(self.display, list())
        webactions = map(self.prepare_webaction, webactions)
        return self._post_formatting(webactions)

    def prepare_webaction(self, action):
        raise NotImplementedError

    def _post_formatting(self, actions):
        return actions


class WebActionsActionsMenuItemsPreparer(BaseWebActionsMenuItemsPreparer):

    display = 'actions-menu'

    def prepare_webaction(self, action):
        return {
                'title': action["title"],
                'description': '',
                'action': action["target_url"],
                'selected': False,
                'icon': None,
                'extra': {
                    # JS event handlers register with an ID selector.
                    'id': "webaction-" + str(action["action_id"]),
                    'separator': None,
                    'class': 'actionicon-object_webaction',
                },
                'submenu': None,
               }

    def _post_formatting(self, actions):
        if len(actions) > 0:
            actions[0]['extra']['separator'] = 'actionSeparator'
        return actions


class WebActionsUserMenuItemsPreparer(BaseWebActionsMenuItemsPreparer):

    display = "user-menu"

    def prepare_webaction(self, action):
        return {
                'title': action["title"],
                'category': 'webactions',
                'url': action["target_url"],
                'separator': None,
                'id': "webaction-" + str(action["action_id"])
               }

    def _post_formatting(self, actions):
        if len(actions) > 0:
            actions[-1]['separator'] = 'actionSeparator'
        return actions


class WebActionsAddMenuItemsPreparer(WebActionsActionsMenuItemsPreparer):

    display = 'add-menu'

    def prepare_webaction(self, action):
        klass = "webaction"
        if action.get("icon_name"):
            klass = "{} {}".format(klass, action.get("icon_name"))

        return {
                'title': action["title"],
                'description': '',
                'action': action["target_url"],
                'selected': False,
                'icon': action.get("icon_data"),
                'extra': {
                    # JS event handlers register with an ID selector.
                    'id': "webaction-" + str(action["action_id"]),
                    'separator': None,
                    'class': klass,
                },
                'submenu': None,
               }
