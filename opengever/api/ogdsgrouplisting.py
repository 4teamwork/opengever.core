from opengever.api.ogdslistingbase import OGDSListingBaseService
from opengever.ogds.models.group import Group
from sqlalchemy.sql.expression import true


class OGDSGroupListingGet(OGDSListingBaseService):
    """API Endpoint that returns groups from ogds.

    GET /@ogds-group-listing HTTP/1.1

    The endpoint returns an object with the same structure as the object
    returned by the @listing endpoint.
    """

    searchable_columns = (
        Group.groupid,
        Group.active,
        Group.title,
        Group.is_local,
    )

    unique_sort_on = 'groupid'
    default_sort_on = 'title'
    model_class = Group
    default_state_filter = tuple()
    default_is_local_filter = tuple()

    def extend_query_with_filters(self, query, filters):
        query = self.extend_query_with_state_filter(query, filters)
        query = self.extend_query_with_is_local_filter(query, filters)
        return query

    def extend_query_with_state_filter(self, query, filters):
        """Implement hardcoded state filter.

        The state filter expects a list of states to be displayed. By default
        it will return all states (active and inacvite groups).
        """
        state = filters.get('state', self.default_state_filter)
        if state == ['active']:
            query = query.filter_by(active=True)
        elif state == ['inactive']:
            query = query.filter_by(active=False)

        return query

    def extend_query_with_is_local_filter(self, query, filters):
        is_local = filters.get('is_local')

        if is_local is True:
            query = query.filter(Group.is_local.is_(true()))
        elif is_local is False:
            # is_local can either be null or false.
            query = query.filter(Group.is_local.isnot(true()))
        return query
