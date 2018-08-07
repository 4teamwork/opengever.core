from opengever.ogds.models.admin_unit import AdminUnit
from opengever.ogds.models.exceptions import RecordNotFound
from opengever.ogds.models.group import Group
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.user import User


class OGDSService(object):

    def __init__(self, session):
        self.session = session

    def find_user(self, userid):
        """returns a User by its userid. When no User is found, this method raises.
           a ValueError.
           See #fetch_user for similar behavior.
        """
        user = self.fetch_user(userid)
        if not user:
            raise RecordNotFound(User, userid)
        return user

    def fetch_user(self, userid):
        """returns a User by it's userid. None is returned when no user is found.
           See #find_user for similar behavior.
        """
        return self._query_user().get(userid)

    def filter_users(self, query_string):
        return self._query_user().by_searchable_text(query_string)

    def all_users(self):
        return self._query_user().all()

    def inactive_users(self):
        return self._query_user().filter_by(active=False).all()

    def assigned_org_units(self, userid):
        query = self._query_org_units().join(OrgUnit.users_group)
        query = query.join(Group.users).filter(User.userid == userid)
        query = query.filter(OrgUnit.enabled==True)
        return query.all()

    def assigned_groups(self, userid):
        query = Group.query.join(Group.users)
        query = query.filter(User.userid == userid)
        return query.all()

    def fetch_org_unit(self, unit_id):
        return self._query_org_units().get(unit_id)

    def all_org_units(self, enabled_only=True):
        query = self._query_org_units()
        if enabled_only:
            query = query.filter_by(enabled=True)

        return query.all()

    def fetch_admin_unit(self, unit_id):
        return self._query_admin_units(enabled_only=False).get(unit_id)

    def all_admin_units(self, enabled_only=True):
        query = self._query_admin_units(enabled_only)
        return query.all()

    def has_multiple_admin_units(self, enabled_only=True):
        query = self._query_admin_units(enabled_only)
        return query.count() > 1

    def has_multiple_org_units(self):
        return self._query_org_units().count() > 1

    def fetch_group(self, groupid):
        return self._query_group().get(groupid)

    def _query_admin_units(self, enabled_only=True):
        query = AdminUnit.query
        if enabled_only:
            query = query.filter_by(enabled=enabled_only)
        return query

    def all_groups(self, active_only=True):
        query = self._query_group()
        if active_only:
            query = query.filter_by(active=True)
        return query.all()

    def _query_org_units(self):
        return OrgUnit.query.order_by(OrgUnit.title)

    def _query_user(self):
        return User.query

    def _query_group(self):
        return Group.query
