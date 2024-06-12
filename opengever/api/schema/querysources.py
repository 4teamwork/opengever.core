from opengever.api.schema.sources import get_field_by_name
from opengever.api.schema.sources import GEVERSourcesGet
from opengever.base.interfaces import IDuringContentCreation
from opengever.workspace import is_workspace_feature_enabled
from opengever.workspace import WHITELISTED_TEAMRAUM_PORTAL_TYPES
from plone.dexterity.utils import iterSchemata
from plone.dexterity.utils import iterSchemataForType
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from Products.CMFPlone.utils import safe_unicode
from z3c.formwidget.query.interfaces import IQuerySource
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.schema.interfaces import ICollection


class GEVERQuerySourcesGet(GEVERSourcesGet):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        super(GEVERQuerySourcesGet, self).__init__(context, request)

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

            # Only allow to access sources of whitelisted portal_types in teamraum.
            # This ensures that the user can't query an unprotected source which exposes
            # userinformation.
            if (is_workspace_feature_enabled() and portal_type not in WHITELISTED_TEAMRAUM_PORTAL_TYPES):
                return self._error(
                    404, "Not Found",
                    "No such field: %r" % fieldname
                )

            schemata = iterSchemataForType(portal_type)
            alsoProvides(self.request, IDuringContentCreation)

        field = get_field_by_name(fieldname, schemata)
        if field is None:
            return self._error(
                404, "Not Found",
                "No such field: %r" % fieldname
            )

        return self.query_and_serialize_results(field, fieldname)

    def query_and_serialize_results(self, field, fieldname):
        bound_field = field.bind(self.context)

        # Look for a source directly on the field first
        source = getattr(bound_field, 'source', None)

        # Handle ICollections (like Tuples, Lists and Sets). These don't have
        # sources themselves, but instead are multivalued, and their
        # items are backed by a value_type of Choice with a source
        if ICollection.providedBy(bound_field):
            source = self._get_value_type_source(bound_field)
            if not source:
                ftype = bound_field.__class__.__name__
                return self._error(
                    404, "Not Found",
                    "%r Field %r does not have a value_type of Choice with "
                    "an IQuerySource" % (ftype, fieldname))

        if not IQuerySource.providedBy(source):
            return self._error(
                404, "Not Found",
                "Field %r does not have an IQuerySource" % fieldname
            )

        query = self.request.form.get("query", None)
        token = self.request.form.get("token", None)
        if not query and not token:
            return self._error(
                400,
                "Bad Request",
                u"Enumerating querysources is not supported. Please search "
                u"the source using the ?query= or ?token = QS parameters"
            )
        if query and token:
            return self._error(
                400,
                "Bad Request",
                u"Please only search the source using either the ?query= or "
                "?token = QS parameters, using both parameters at the same "
                "time is unsupported"
            )

        if query:
            if getattr(source, 'provides_raw_queries', False):
                result = RawQuerySourceSearchResults(
                    source, source.raw_search(safe_unicode(query)))
            else:
                result = ResolvedQuerySourceSearchResults(source.search(safe_unicode(query)))
        else:
            try:
                result = ResolvedQuerySourceSearchResults(
                    [source.getTermByToken(safe_unicode(token))])
            except LookupError:
                result = ResolvedQuerySourceSearchResults([])

        terms = []
        for term in result.results:
            terms.append(term)

        batch = HypermediaBatch(self.request, terms)

        serialized_terms = []
        for term in batch:
            serializer = getMultiAdapter(
                (result.get_resolved_term(term), self.request), interface=ISerializeToJson
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


class RawQuerySourceSearchResults():
    def __init__(self, source, results):
        self.results = results
        self.source = source

    def get_resolved_term(self, term):
        return self.source.getTerm(term.token)


class ResolvedQuerySourceSearchResults():
    def __init__(self, results):
        self.results = results

    def get_resolved_term(self, term):
        return term
