from plone.app.contentlisting.interfaces import IContentListingObject
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.summary import DefaultJSONSummarySerializer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJsonSummary)
@adapter(Interface, Interface)
class TodoJSONSummarySerializer(DefaultJSONSummarySerializer):

    def __call__(self):
        if hasattr(self.context, 'getObject'):
            obj = self.context.getObject()
        else:
            obj = self.context

        return json_compatible({
            '@id': obj.absolute_url(),
            '@type': obj.portal_type,
            'id': obj.getId(),
            'title': obj.Title(),
            'due_date': obj.due_date,
        })
