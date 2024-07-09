from opengever.activity import notification_center
from opengever.activity.roles import WATCHER_ROLE
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.sources import AllFilteredGroupsSourcePrefixed
from opengever.ogds.base.sources import AllTeamsSource
from opengever.ogds.base.sources import AssignedUsersSource
from opengever.ogds.base.sources import BaseMultipleSourcesQuerySource
from opengever.ogds.models.group import Group
from opengever.ogds.models.team import Team
from opengever.ogds.models.user import User
from plone import api
from sqlalchemy import case


def get_watcher_ids(context):
    """Returns all ids of actors watching the current context
    """
    return [watcher.actorid for watcher in
            notification_center().get_watchers(context, role=WATCHER_ROLE)]


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
        query = self._filter_not_subscribing_watchers(query)
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

    def _filter_not_subscribing_watchers(self, query):
        """This function adds the filter clause to only return users without a
        watcher-role on the current context.
        """
        query = query.filter(User.userid.notin_(get_watcher_ids(self.context)))
        return query


class PossibleWatchersSourceGroups(AllFilteredGroupsSourcePrefixed):
    """A vocabulary source of all groups not watching the current context
    """
    @property
    def base_query(self):
        query = super(PossibleWatchersSourceGroups, self).base_query
        return self._filter_not_subscribing_watchers(query)

    @property
    def search_query(self):
        query = super(PossibleWatchersSourceGroups, self).search_query
        return self._filter_not_subscribing_watchers(query)

    def _filter_not_subscribing_watchers(self, query):
        """This function adds the filter clause to only return groups without a
        watcher-role on the current context.
        """
        group_ids = [watcher.split(':', 1)[-1] for watcher
                     in get_watcher_ids(self.context)
                     if watcher.startswith(self.GROUP_PREFIX)]
        query = query.filter(Group.groupid.notin_(group_ids))
        return query


class PossibleWatchersSourceTeams(AllTeamsSource):
    """A vocabulary source of all teams not watching the current context
    """
    @property
    def search_query(self):
        query = super(PossibleWatchersSourceTeams, self).search_query
        return self._filter_not_subscribing_watchers(query)

    def _filter_not_subscribing_watchers(self, query):
        """This function adds the filter clause to only return teams without a
        watcher-role on the current context.
        """
        team_ids = [watcher.split(':', 1)[-1] for watcher
                    in get_watcher_ids(self.context)
                    if ActorLookup(watcher).is_team()]
        query = query.filter(Team.team_id.notin_(team_ids))
        return query


class PossibleWatchersSource(BaseMultipleSourcesQuerySource):
    """A vocabulary source of all users, groups and teams not watching a
    ressource assigned to the current admin unit.
    """

    def __init__(self, context):
        self.context = context
        self.terms = []
        self.source_instances = [PossibleWatchersSourceUsers(context),
                                 PossibleWatchersSourceGroups(context),
                                 PossibleWatchersSourceTeams(context)]
