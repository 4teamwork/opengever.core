from opengever.base.interfaces import IBaseSettings
from opengever.ogds.base.sources import AllFilteredGroupsSourcePrefixed
from opengever.ogds.base.sources import AllTeamsSource
from opengever.ogds.base.sources import AssignedUsersSource
from opengever.ogds.base.sources import BaseMultipleSourcesQuerySource
from opengever.ogds.models.user import User
from opengever.workspace import is_workspace_feature_enabled
from plone import api
from sqlalchemy import case
import re


class PossibleWatchersSourceUsers(AssignedUsersSource):
    """A vocabulary source of all users not watching a ressource assigned
    to the current admin unit.

    The results are sorted by the last and first name in general. Beside of
    this sorting, the current user will be always at the first position if
    available.
    """

    search_only_active_users = True

    @property
    def base_query(self):
        query = super(PossibleWatchersSourceUsers, self).base_query
        return self._extend_query(query)

    @property
    def search_query(self):
        query = super(PossibleWatchersSourceUsers, self).search_query
        return self._extend_query(query)

    def _extend_query(self, query):
        query = self._current_user_first(query)
        return query

    def _current_user_first(self, query):
        """The current user have to be at first position if available.

        This function extends the query with the order_by clause to move
        the current user to the first position if available.
        """
        current_user = api.user.get_current()
        return query.order_by(case(
            ((User.userid == current_user.getId(), 1), ),
            else_=2))


class PossibleWatchersGroupsSource(AllFilteredGroupsSourcePrefixed):

    def terms_filter(self, term):
        white_list_prefix = api.portal.get_registry_record(
            'possible_watcher_groups_white_list_regex', IBaseSettings)
        return bool(re.search(white_list_prefix, term.value))


class PossibleWatchersSource(BaseMultipleSourcesQuerySource):
    """A vocabulary source of all users, groups and teams not watching a
    ressource assigned to the current admin unit.
    """
    gever_only = False

    def __init__(self, context):
        self.context = context
        self.terms = []

        self.source_instances = [PossibleWatchersSourceUsers(context),
                                 PossibleWatchersGroupsSource(context)]

        if not is_workspace_feature_enabled():
            self.source_instances.append(AllTeamsSource(context))
