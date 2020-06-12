from opengever.ogds.base.sources import AssignedUsersSource
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFPlone.utils import safe_unicode
from zope.component import getMultiAdapter


class AssignedUsersGet(Service):
    def reply(self):
        source = AssignedUsersSource(self.context)
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
