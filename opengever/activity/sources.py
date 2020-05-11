from opengever.activity import notification_center
from opengever.ogds.base.sources import AssignedUsersSource
from opengever.ogds.models.user import User
from plone import api
from sqlalchemy import case


class PossibleWatchersSource(AssignedUsersSource):
    """A vocabulary source of all users not watching a ressource assigned
    to the current admin unit.

    The results are sorted by the last and first name in general. Beside of
    this sorting, the current user will be always at the first position if
    available.
    """

    @property
    def base_query(self):
        query = super(PossibleWatchersSource, self).base_query
        return self._extend_query(query)

    @property
    def search_query(self):
        query = super(PossibleWatchersSource, self).search_query
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
            else_='2'))

    def _filter_not_subscribing_watchers(self, query):
        """This function adds the filter clause to only return users without a
        watcher-role on the current context.
        """
        center = notification_center()
        regular_watchers = center.get_subscriptions(self.context)
        userids = set([subscription.watcher.actorid for subscription in regular_watchers])

        if userids:
            query = query.filter(User.userid.notin_(userids))
        return query
