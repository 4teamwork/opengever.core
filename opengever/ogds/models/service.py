from opengever.base.model import create_session
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.ogds.models.exceptions import RecordNotFound
from opengever.ogds.models.group import Group
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.user import User
from plone import api


def ogds_service():
    return OGDSService(create_session())


class OGDSService(object):

    def __init__(self, session):
        self.session = session

    def _get_current_user_id(self):
        return api.user.get_current().getId()

    def fetch_current_user(self):
        userid = self._get_current_user_id()
        return self.fetch_user(userid) if userid else None

    def find_user(self, userid):
        """Returns a User by its userid. When no User is found, this method raises.
        a ValueError.

        See #fetch_user for similar behavior.
        """
        user = self.fetch_user(userid)
        if not user:
            raise RecordNotFound(User, userid)
        return user

    def fetch_user_by_username(self, username):
        """Returns a User by it's username. When no user or multiple are found,
        this method raises.
        """
        return self._query_user().filter_by(username=username).first()

    def fetch_user(self, userid, username_as_fallback=False):
        """Returns a User by it's userid. None is returned when no user is found.

        See #find_user for similar behavior.
        """
        user = self._query_user().get(userid)
        if not user and username_as_fallback:
            user = self.fetch_user_by_username(userid)

        return user

    def filter_users(self, query_string):
        return self._query_user().by_searchable_text(query_string)

    def all_users(self):
        return self._query_user().all()

    def inactive_users(self):
        return self._query_user().filter_by(active=False).all()

    def assigned_org_units(self, userid=None, omit_current=False):
        if userid is None:
            userid = self._get_current_user_id()

        query = self._query_org_units(
            enabled_only=True, visible_only=True).join(OrgUnit.users_group)

        query = query.join(Group.users).filter(User.userid == userid)
        org_units = query.all()

        if omit_current:
            # Avoid circular imports
            from opengever.ogds.base.utils import get_current_org_unit
            current_org_unit = get_current_org_unit()
            org_units = [each for each in org_units
                         if each != current_org_unit]
        return org_units

    def fetch_org_unit(self, unit_id):
        return self._query_org_units(
            enabled_only=False, visible_only=False).get(unit_id)

    def all_org_units(self, enabled_only=True, visible_only=True):
        query = self._query_org_units(enabled_only=enabled_only,
                                      visible_only=visible_only)
        return query.all()

    def fetch_admin_unit(self, unit_id):
        return self._query_admin_units(
            enabled_only=False, visible_only=False).get(unit_id)

    def all_admin_units(self, enabled_only=True, visible_only=True, omit_current=False):
        query = self._query_admin_units(enabled_only=enabled_only,
                                        visible_only=visible_only,
                                        omit_current=omit_current)
        return query.all()

    def has_multiple_admin_units(self, enabled_only=True, visible_only=True):
        query = self._query_admin_units(enabled_only=enabled_only,
                                        visible_only=visible_only)
        return query.count() > 1

    def has_multiple_org_units(self):
        query = self._query_org_units(enabled_only=False, visible_only=False)
        return query.count() > 1

    def fetch_group(self, groupid, groupname_as_fallback=False):
        group = self._query_group().get(groupid)
        if not group and groupname_as_fallback:
            group = self.fetch_group_by_groupname(groupid)

        return group

    def fetch_group_by_groupname(self, groupname):
        return self._query_group().filter_by(groupname=groupname).first()

    def _query_admin_units(self, enabled_only=True, visible_only=True, omit_current=False):
        query = AdminUnit.query
        if enabled_only:
            query = query.filter_by(enabled=True)
        if visible_only:
            query = query.filter_by(hidden=False)
        if omit_current:
            # Avoid circular imports
            from opengever.ogds.base.utils import get_current_admin_unit
            current_admin_unit = get_current_admin_unit()
            query = query.filter(AdminUnit.unit_id != current_admin_unit.unit_id)
        return query

    def all_groups(self, active_only=True):
        query = self._query_group()
        if active_only:
            query = query.filter_by(active=True)
        return query.all()

    def _query_org_units(self, enabled_only=True, visible_only=True):
        query = OrgUnit.query
        if enabled_only:
            query = query.filter_by(enabled=True)
        if visible_only:
            query = query.filter_by(hidden=False)
        return query.order_by(OrgUnit.title)

    def _query_user(self):
        return User.query

    def _query_group(self):
        return Group.query
