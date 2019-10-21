from opengever.api.schema.sources import get_field_by_name
from opengever.api.schema.sources import GEVERSourcesGet
from plone.dexterity.utils import iterSchemata
from plone.dexterity.utils import iterSchemataForType
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from z3c.formwidget.query.interfaces import IQuerySource
from zope.component import getMultiAdapter


class GEVERQuerySourcesGet(GEVERSourcesGet):

    def reply(self):
        if len(self.params) not in (1, 2):
            return self._error(
                400, "Bad Request",
                "Must supply either one (fieldname) or two (portal_type, fieldname) parameters"
            )

        if len(self.params) == 1:
            # Edit intent
            # - context is the object to be edited
            # - schemata need to be determined via context
            self.intent = 'edit'
            portal_type = None
            fieldname = self.params[0]
            schemata = iterSchemata(self.context)

        else:
            # Add intent
            # - context is the container where the object will be created
            # - portal_type is the type of object to be created
            # - schemata need to be determined via portal_type
            self.intent = 'add'
            portal_type = self.params[0]
            fieldname = self.params[1]
            schemata = iterSchemataForType(portal_type)

        field = get_field_by_name(fieldname, schemata)
        if field is None:
            return self._error(
                404, "Not Found",
                "No such field: %r" % fieldname
            )
        bound_field = field.bind(self.context)

        source = bound_field.source
        if not IQuerySource.providedBy(source):
            return self._error(
                404, "Not Found",
                "Field %r does not have an IQuerySource" % fieldname
            )

        if 'query' not in self.request.form:
            return self._error(
                400, "Bad Request",
                u'Enumerating querysources is not supported. Please search '
                u'the source using the ?query= QS parameter'
            )

        query = self.request.form['query']

        result = source.search(query)

        terms = []
        for term in result:
            terms.append(term)

        batch = HypermediaBatch(self.request, terms)

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
