from Acquisition import aq_base
from Acquisition import aq_inner
from collections import defaultdict
from opengever.base.model import create_session
from opengever.base.public_permissions import PUBLIC_PERMISSIONS_MAPPING
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from opengever.webactions.interfaces import IWebActionsProvider
from opengever.webactions.storage import get_storage
from plone import api
from plone.dexterity.interfaces import IDexterityContent
from plone.memoize.view import memoize_contextless
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(IWebActionsProvider)
@adapter(IDexterityContent, IBrowserRequest)
class WebActionsProvider(object):
    """Default IWebActionsProvider implementation.

    Returns a list of webactions for a given user on a given context.
    Only webactions matching the following criteria are returned:
      - action is enabled.
      - action scope is global.
      - if 'types' field is not empty, the context portal_type must be one
        of the types in the list.
      - if 'permissions' field is not empty, user must have at least one of
        the given permission on the context.
      - if 'groups' field is not empty, user must be at least in one of the
        given groups.

    Actions are returned sorted according to the 'order' field and 'title'.
    """

    _attributes_to_keep = ("title", "target_url", "mode", "action_id",
                           "icon_name", "icon_data", "display")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _list_all_actions(self):
        return get_storage().list()

    @staticmethod
    def _action_enabled(action):
        return action.get("enabled", True)

    def _action_satisfies_types(self, action):
        types = action.get("types")
        if not types:
            return True
        return aq_base(aq_inner(self.context)).portal_type in types

    @memoize_contextless
    def _get_permissions(self, username):
        permissions = api.user.get_permissions(username=username, obj=self.context)
        return set(name for name, value in permissions.items() if value)

    def _action_satisfies_permissions(self, action):
        action_permissions = action.get("permissions")
        if not action_permissions:
            return True
        action_permissions = map(PUBLIC_PERMISSIONS_MAPPING.get, action_permissions)
        username = api.user.get_current().getUserName()
        user_permissions = self._get_permissions(username)
        return any(permission in user_permissions
                   for permission in action_permissions)

    @memoize_contextless
    def _user_in_any_of_groups(self, userid, group_ids):
        stmt = Group.query.join(Group.users).filter(
            User.userid == userid,
            Group.groupid.in_(group_ids)
        ).exists()
        return create_session().query(stmt).scalar()

    def _action_satisfies_groups(self, action):
        action_groups = action.get("groups")
        if not action_groups:
            return True

        userid = api.user.get_current().getId()
        return self._user_in_any_of_groups(userid, tuple(action_groups))

    def _action_satisfies_scope(self, action):
        # XXX Not sure what the logic will be with the scope argument
        # This will need to be adapted when we implement the other possible
        # scopes
        scope = action.get("scope")
        if scope == "global":
            return True
        elif scope == "context":
            intid = getUtility(IIntIds).getId(self.context)
            return intid in get_storage().get_context_intids(action['action_id'])
        return False

    def _action_should_be_provided_on_context(self, action):
        return (self._action_enabled(action)
                and self._action_satisfies_types(action)
                and self._action_satisfies_scope(action))

    def _action_should_be_provided_for_user(self, action):
        return (self._action_satisfies_permissions(action)
                and self._action_satisfies_groups(action))

    @memoize_contextless
    def _get_webactions_for_context(self):
        # XXX This could be easily cached more long term with just the context
        # and a timestamp of the last modification of the storage as key.
        action_list = get_storage().list()
        return filter(self._action_should_be_provided_on_context, action_list)

    def _filter_for_display(self, display, action_list):
        return filter(lambda action: action["display"] == display,
                      action_list)

    def _filter_for_user(self, action_list):
        return filter(self._action_should_be_provided_for_user, action_list)

    @staticmethod
    def _sort_key(action):
        return (action.get("order"), action.get("title"))

    def _sort(self, action_list):
        return sorted(action_list, key=self._sort_key)

    def _filter_action_data(self, action):
        return dict((key, action.get(key)) for key in self._attributes_to_keep)

    def get_webactions(self, display=None, flat=False):
        webactions = self._get_webactions_for_context()
        if display is not None:
            webactions = self._filter_for_display(display, webactions)
        webactions = self._sort(self._filter_for_user(webactions))

        if flat:
            return map(self._filter_action_data, webactions)

        webactions_dict = defaultdict(list)
        for webaction in webactions:
            webactions_dict[webaction["display"]].append(
                self._filter_action_data(webaction))
        return webactions_dict
