from opengever.ogds.base.sources import WorkspaceContentMemberGroupsSource
from opengever.ogds.base.sources import WorkspaceContentMemberUsersSource
from opengever.workspace.utils import is_within_workspace
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFPlone.utils import safe_unicode
from zExceptions import BadRequest
from zExceptions import Forbidden
from zope.component import getMultiAdapter


class WorkspaceContentMembersGet(Service):
    def reply(self):
        if not is_within_workspace(self.context):
            raise BadRequest("'{}' is not within a workspace".format(self.context.getId()))

        if not self.context.access_members_allowed():
            raise Forbidden

        source = WorkspaceContentMemberUsersSource(self.context)
        query = safe_unicode(self.request.form.get('query', ''))
        results = source.search(query)

        if self.request.form.get('include_groups'):
            group_source = WorkspaceContentMemberGroupsSource(self.context)
            group_results = group_source.search(query)
            results.extend(group_results)

        batch = HypermediaBatch(self.request, results)

        serialized_terms = []
        for term in batch:
            serializer = getMultiAdapter(
                (term, self.request), interface=ISerializeToJson
            )
            serialized_terms.append(serializer())

        result = {
            "@id": batch.canonical_url,
            "items": serialized_terms,
            "items_total": batch.items_total,
        }
        links = batch.links
        if links:
            result["batching"] = links
        return result
