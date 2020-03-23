from opengever.api.ogdslistingbase import OGDSListingBaseService
from opengever.ogds.models.user import User


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
        return query
