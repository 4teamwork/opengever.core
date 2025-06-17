from opengever.base.interfaces import IBaseSettings
from opengever.ogds.base.sources import AllFilteredGroupsSourcePrefixed
from opengever.ogds.base.sources import AllTeamsSource
from opengever.ogds.base.sources import AssignedUsersSource
from opengever.ogds.base.sources import BaseMultipleSourcesQuerySource
from opengever.ogds.models.group import groups_users
from opengever.ogds.models.service import ogds_service
from opengever.ogds.models.user import User
from opengever.workspace import is_workspace_feature_enabled
from plone import api
from Products.CMFCore.interfaces import IIndexableObject
from sqlalchemy import case
from sqlalchemy.sql import select
from zope.component import queryMultiAdapter
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
        query = self.restrict_whitelisted_principals(query)
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

    def restrict_whitelisted_principals(self, query):
        """Only principals having View permission on the context are meant as
        possible watchers.
        """
        return query.filter(User.userid.in_(self.get_whitelisted_principals()))

    def get_whitelisted_principals(self):
        """Returns a set of user-ids having direct or indirect (through groups)
        View-permission on the current context.
        """
        allowed_users_and_groups = self.extract_allowed_users_and_groups()
        allowed_users_and_groups.update(
            self.extract_group_members(allowed_users_and_groups))
        return allowed_users_and_groups

    def extract_allowed_users_and_groups(self):
        """Extracts all userids with View-permission on the given context
        """
        indexable_object = queryMultiAdapter(
            (self.context, api.portal.get_tool('portal_catalog')),
            IIndexableObject)

        if not indexable_object:
            return set()

        return {
            index_value.split('user:')[-1]
            for index_value in indexable_object.allowedRolesAndUsers
            if index_value.startswith('user:')
        }

    def extract_group_members(self, groupids):
        """Returns all group members (userids) of the given groupids.
        """
        return {
            userid
            for userid, in ogds_service()
            .session.execute(
                select([groups_users.c.userid], groups_users.c.groupid.in_(groupids))
            )
            .fetchall()
        }


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
            self.source_instances.append(AllTeamsSource(context,
                                                        only_current_orgunit=True))
