from ftw.solr.interfaces import ISolrSearch
from opengever.api.solr_query_service import SolrQueryBaseService
from plone import api
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class AccessibleWorkspacesGet(SolrQueryBaseService):
    """API Endpoint that returns the accessible workspaces for a single actor.

    GET /@accessible-workspaces/actor-id HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(AccessibleWorkspacesGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after service name as parameters
        self.params.append(name)
        return self

    def reply(self):
        userid = self.read_params().decode('utf-8')
        user = api.user.get(userid)
        if not user:
            raise BadRequest(u'Invalid userid "{}".'.format(userid))

        allowed_roles_and_users = [u'user:{}'.format(userid)]
        allowed_roles_and_users.extend([u'user:{}'.format(group) for group in user.getGroups()])
        allowed_roles_and_users.extend(user.getRoles())

        query = u'object_provides:opengever.workspace.interfaces.IWorkspace'

        field = self.get_field('allowedRolesAndUsers')
        solr_filter = field.listing_to_solr_filter(allowed_roles_and_users)

        solr = getUtility(ISolrSearch)
        response = solr.unrestricted_search(query=query, filters=solr_filter,
                                            sort='sortable_title asc')

        self.response_fields = {'@id', '@type', 'review_state', 'title'}
        result = {
            '@id': '{}/@accessible-workspaces/{}'.format(api.portal.get().absolute_url(), userid),
            'items': self.prepare_response_items(response),

        }
        return result

    def read_params(self):
        if len(self.params) == 0:
            raise BadRequest('Must supply a userid as URL path parameter.')

        if len(self.params) > 1:
            raise BadRequest('Only userid is supported URL path parameter.')

        return self.params[0]
