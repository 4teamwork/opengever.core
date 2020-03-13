from opengever.api.ogdslistingbase import OgdsListingBaseService
from opengever.ogds.models.user import User
from ZPublisher.HTTPRequest import record


class UserListingGet(OgdsListingBaseService):
    """API Endpoint that returns users from ogds.

    GET /@user-listing HTTP/1.1

    The endpoint returns an object with the same structure as the object
    returned by the @listing endpoint.
    """

    item_columns = (
        'active',
        'department',
        'directorate',
        'email',
        'firstname',
        'firstname',
        'lastname',
        'phone_office',
        'userid',
    )

    searchable_columns = (
        User.lastname,
        User.firstname,
        User.userid,
        User.email,
        User.phone_office,
        User.department,
        User.directorate,
    )

    default_sort_on = 'lastname'
    model_class = User
    default_state_filter = tuple()

    def fill_item(self, item, model):
        item = super(UserListingGet, self).fill_item(item, model)
        item['@type'] = 'virtual.ogds.user'
        item['title'] = model.fullname()
        item['@id'] = '{}/@ogds-user/{}'.format(
            self.context.absolute_url(), model.userid)
        return item

    def extend_query_with_filters(self, query, params):
        """Implement hardcoded state filter.

        The state filter expects a list of states to be displayed. By default
        it will return all states (active and inacvite users).
        """
        filters = params.get('filters', {})
        if not isinstance(filters, record):
            filters = {}

        state = filters.get('state', self.default_state_filter)
        if state == ['active']:
            query = query.filter_by(active=True)
        elif state == ['inactive']:
            query = query.filter_by(active=False)
        return query
