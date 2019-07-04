from opengever.base.interfaces import IOpengeverBaseLayer
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.summary import BLACKLISTED_ATTRIBUTES
from plone.restapi.serializer.summary import DefaultJSONSummarySerializer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

@implementer(ISerializeToJsonSummary)
@adapter(Interface, IOpengeverBaseLayer)
class GeverJSONSummarySerializer(DefaultJSONSummarySerializer):
    """Customized ISerializeToJsonSummary adapter for GEVER.

    We need to extend the FIELD_ACCESSORS list with some additional accessors.
    Unfortunately the FIELD_ACCESSORS list is not part of the the
    DefaultJSONSummarySerializer class, so we also need to overwrite the
    __call__ method to use our won list.
    """

    FIELD_ACCESSORS = {
        "@id": "getURL",
        "@type": "PortalType",
        "description": "Description",
        "title": "Title",
        "mimetype": "getContentType",
        "creator": "Creator",
        "reference_number": "reference"
    }

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        obj = IContentListingObject(self.context)
        summary = {}
        for field in self.metadata_fields():
            if field.startswith("_") or field in BLACKLISTED_ATTRIBUTES:
                continue
            accessor = self.FIELD_ACCESSORS.get(field, field)
            value = getattr(obj, accessor, None)
            if callable(value):
                value = value()
            summary[field] = json_compatible(value)
        return summary
