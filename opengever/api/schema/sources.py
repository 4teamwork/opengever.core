# -*- coding: utf-8 -*-
from opengever.base.interfaces import IDuringContentCreation
from plone.dexterity.utils import iterSchemata
from plone.dexterity.utils import iterSchemataForType
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services.sources.get import SourcesGet
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IIterableSource
from zope.schema.interfaces import ISource


class GEVERSourcesGet(SourcesGet):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        super(GEVERSourcesGet, self).__init__(context, request)

    def publishTraverse(self, request, name):
        # Treat any path segments after /@sources as parameters
        self.params.append(name)
        return self

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
            alsoProvides(self.request, IDuringContentCreation)

        field = get_field_by_name(fieldname, schemata)
        if field is None:
            return self._error(
                404, "Not Found",
                "No such field: %r" % fieldname
            )

        bound_field = field.bind(self.context)

        source = bound_field.source
        if not ISource.providedBy(source):
            return self._error(
                404, "Not Found",
                "Field %r does not have a source" % fieldname
            )

        if not IIterableSource.providedBy(source):
            return self._error(
                400, "Bad Request",
                "Source for field %r is not iterable. " % fieldname
            )

        serializer = getMultiAdapter(
            (source, self.request), interface=ISerializeToJson
        )
        return serializer(
            "{}/@sources/{}".format(self.context.absolute_url(), fieldname)
        )


def get_field_by_name(fieldname, schemata):
    for schema in schemata:
        fields = getFieldsInOrder(schema)
        for fn, field in fields:
            if fn == fieldname:
                return field
