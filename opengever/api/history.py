from datetime import datetime as dt
from opengever.api.actors import serialize_actor_id_to_json_summary
from opengever.document.approvals import IApprovalList
from opengever.document.browser.versions_tab import LazyHistoryMetadataProxy
from opengever.document.browser.versions_tab import NoVersionHistoryMetadataProxy
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.ogds.base.actor import Actor
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.restapi.services.history.get import HistoryGet
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite


class HistoryPatch(Service):
    """ Copy of the plone.restapi.services.HistoryPatch but uses
    the ICheckinCheckoutManager to revert to an older file
    version instead of the portal_repository tool.
    """

    def reply(self):
        body = json_body(self.request)
        version = body["version"]

        # revert the file
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)
        manager.revert_to_version(version)

        title = self.context.title_or_id()
        msg = u"{} has been reverted to revision {}.".format(title, version)

        return json_compatible({"message": msg})


class GeverHistoryGet(HistoryGet):
    """ We overwrite the history endpoint to always use the creator as the
    actor of the initial version. There were situations in the past where the
    creator of the initial version was not set correctly, or where the initial
    version is missing altogether (see
    https://github.com/4teamwork/opengever.core/pull/4632 and
    https://github.com/4teamwork/opengever.core/pull/6935).
    """
    def reply(self):
        if self.version:
            return super(GeverHistoryGet, self).reply()

        history = super(GeverHistoryGet, self).reply()
        versions = [entry for entry in history if entry['type'] == 'versioning']
        if not versions:
            return history

        initial_version = versions[-1]
        if initial_version['actor']['id'] == self.context.Creator():
            return history

        site_url = getSite().absolute_url()
        actorid = self.context.Creator()
        actor = Actor.lookup(actorid)

        initial_version['actor'] = {
                "@id": "{}/@users/{}".format(site_url, actorid),
                "id": actorid,
                "fullname": actor.get_label(with_principal=False),
                "username": None,
            }

        return json_compatible(history)


class VersionsGet(HistoryGet):

    def reply(self):
        # Traverse to historical version
        if self.version:
            serializer = queryMultiAdapter(
                (self.context, self.request), ISerializeToJson
            )
            data = serializer(version=self.version)
            return data

        # Listing historical data (versions only)
        shadow_history = Versioner(self.context).get_history_metadata()
        manager = getMultiAdapter((self.context, self.request), ICheckinCheckoutManager)

        if not shadow_history:
            history = NoVersionHistoryMetadataProxy(self.context)

        else:
            history = LazyHistoryMetadataProxy(
                shadow_history, self.context.absolute_url(),
                self.context, is_revert_allowed=manager.is_revert_allowed())

        batch = HypermediaBatch(self.request, history)
        approvals = IApprovalList(self.context).get_grouped_by_version_id()

        versions = []
        for item in batch:
            versions.append({
                "@id": "{}/@versions/{}".format(
                    self.context.absolute_url(), item.version),
                "version": item.version,
                "actor": serialize_actor_id_to_json_summary(item.actor_id),
                "may_revert": item.is_revert_allowed,
                "comments": item.comment,
                "time": dt.fromtimestamp(item.raw_timestamp).isoformat(),
                "approvals": json_compatible(approvals.get(item.version, []))
            })

        result = {
            "@id": batch.canonical_url,
            "items": versions,
            "items_total": batch.items_total,
        }
        links = batch.links
        if links:
            result["batching"] = links

        return result
