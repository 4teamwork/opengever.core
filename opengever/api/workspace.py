import plone.protect.interfaces
from Products.CMFPlone.utils import safe_unicode
from plone import api
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface import implementer
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.sources import ActualWorkspaceMembersSource
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.participation import can_manage_member


@implementer(ISerializeToJson)
@adapter(IWorkspace, Interface)
class SerializeWorkspaceToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeWorkspaceToJson, self).__call__(*args, **kwargs)

        result[u"can_manage_participants"] = can_manage_member(self.context)

        user_id = self.context.Creator()
        actor = Actor.lookup(user_id)
        result["responsible"] = {
            "title": actor.get_label(),
            "token": user_id,
        }
        result["responsible_fullname"] = actor.get_label(with_principal=False)

        return result


class ChangeResponsible(Service):
    """
    The responsible of a workspace is its creator (in Plone). Use this
    endpoint to set a different responsible of a workspace.
    """

    def reply(self):
        userid = self.extract_user_id()

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        self.context.setCreators(userid)

        # Creator is not an index, only metadata. So we reindex UID which is a cheap index. Otherwise
        # we end up indexing everything,.
        self.context.reindexObject(idxs=["UID", "Creator"])

        self.request.response.setStatus(204)
        return super(ChangeResponsible, self).reply()

    def extract_user_id(self):
        data = json_body(self.request)
        userid = data.get("userid", None)
        if not userid:
            raise BadRequest("Property 'userid' is required")
        if not api.user.get(userid):
            raise BadRequest("userid '{}' does not exist".format(userid))
        return userid


class PossibleWorkspaceResponsibles(Service):
    def reply(self):
        source = ActualWorkspaceMembersSource(self.context)
        query = safe_unicode(self.request.form.get('query', ''))
        results = source.search(query)

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
