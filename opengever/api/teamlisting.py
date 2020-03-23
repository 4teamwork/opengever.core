from opengever.api.ogdslistingbase import OGDSListingBaseService
from opengever.ogds.models.team import Team


class TeamListingGet(OGDSListingBaseService):
    """API Endpoint that returns teams from ogds.

    GET /@team-listing HTTP/1.1

    The endpoint returns an object with the same structure as the object
    returned by the @listing endpoint.
    """

    searchable_columns = (
        Team.title,
        Team.groupid,
        Team.org_unit_id,
    )

    default_sort_on = 'title'
    model_class = Team
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
