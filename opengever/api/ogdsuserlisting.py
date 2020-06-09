from datetime import datetime
from opengever.api.ogdslistingbase import OGDSListingBaseService
from opengever.ogds.models.user import User

import re


class OGDDSUserListingGet(OGDSListingBaseService):
    """API Endpoint that returns users from ogds.

    GET /@ogds-user-listing HTTP/1.1

    The endpoint returns an object with the same structure as the object
    returned by the @listing endpoint.
    """

    searchable_columns = (
        User.lastname,
        User.firstname,
        User.userid,
        User.email,
        User.email2,
        User.phone_office,
        User.phone_mobile,
        User.phone_fax,
        User.department,
        User.directorate,
    )

    default_sort_on = 'lastname'
    model_class = User
    default_state_filter = tuple()
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2}) TO (\d{4}-\d{2}-\d{2})")

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
        return query
