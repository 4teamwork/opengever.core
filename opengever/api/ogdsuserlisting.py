from datetime import datetime
from opengever.api.ogdslistingbase import OGDSListingBaseService
from opengever.base.visible_users_and_groups_filter import visible_users_and_groups_filter
from opengever.ogds.models.group import GroupMembership
from opengever.ogds.models.group import groups_users
from opengever.ogds.models.user import User
import re


class OGDSUserListingGet(OGDSListingBaseService):
    """API Endpoint that returns users from ogds.

    GET /@ogds-user-listing HTTP/1.1

    The endpoint returns an object with the same structure as the object
    returned by the @listing endpoint.
    """

    searchable_columns = (
        User.lastname,
        User.firstname,
        User.userid,
        User.username,
        User.email,
        User.email2,
        User.phone_office,
        User.phone_mobile,
        User.phone_fax,
        User.department,
        User.directorate,
    )

    unique_sort_on = 'userid'
    default_sort_on = 'lastname'
    model_class = User
    default_state_filter = tuple()
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2}) TO (\d{4}-\d{2}-\d{2})")

    def reply(self):
        result = super(OGDSUserListingGet, self).reply()
        filters = self.request.form.get('filters', {})

        self._augment_items_with_membership_note(result, filters)
        return result

    def needs_join_with_groups_users(self, filters):
        return bool(filters.get('groupid', False))

    def _convert_date_query_to_dates(self, date_query):
        search = self.pattern.search(date_query)
        start, end = search.group(1), search.group(2)
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        return start_date, end_date

    def extend_query_with_filters(self, query, filters):
        """Implement hardcoded state filter.

        The state filter expects a list of states to be displayed. By default
        it will return all states (active and inacvite users).
        """
        state = filters.get('state', self.default_state_filter)
        if state == ['active']:
            query = query.filter_by(active=True)
        elif state == ['inactive']:
            query = query.filter_by(active=False)
        last_login_query = filters.get('last_login', None)
        if last_login_query:
            start_date, end_date = self._convert_date_query_to_dates(last_login_query[0])
            query = query.filter(User.last_login >= start_date, User.last_login <= end_date)

        if self.needs_join_with_groups_users(filters):
            groupid = filters.get('groupid', None)
            query = query.join(groups_users).filter_by(groupid=groupid)

        query = self.extend_query_with_visible_users_and_groups_filter(query)

        return query

    def extend_query_with_visible_users_and_groups_filter(self, query):
        if not visible_users_and_groups_filter.can_access_all_principals():
            query = query.filter(self.model_class.userid.in_(
                visible_users_and_groups_filter.get_whitelisted_principals()))

        return query

    def _augment_items_with_membership_note(self, result, filters):
        groupid = filters.get('groupid', None)
        items = result.get('items') or []

        userids = list({item.get('userid') for item in items})
        if not userids:
            return

        rows = (
            GroupMembership.query
            .with_entities(GroupMembership.userid, GroupMembership.note)
            .filter(
                GroupMembership.groupid == groupid,
                GroupMembership.userid.in_(userids),
                GroupMembership.note.isnot(None),
            )
            .all()
        )
        notes_by_userid = dict(rows)

        for item in items:
            uid = item.get('userid')
            if not uid:
                continue
            note = notes_by_userid.get(uid)
            if note:
                item['note'] = note
