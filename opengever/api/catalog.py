from opengever.base.interfaces import IOpengeverBaseLayer
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.catalog import BrainSerializer
from Products.ZCatalog.interfaces import ICatalogBrain
from zope.component import adapter
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(ICatalogBrain, IOpengeverBaseLayer)
class GeverBrainSerializer(BrainSerializer):
    """Provides support for some additional metadata attributes provided by
    the CatalogContentListingObject.
    """

    # A list of supported metadata attributes not directly available on
    # the catalog object itself, but accessible on the contentlisting object.
    # The getter of those attributes must be perfomance ,
    # because its processed for each search result.
    CONTENTLISTING_METADATA = [
        'get_preview_pdf_url',
        'get_preview_image_url',
    ]

    def __call__(self, metadata_fields=('_all',)):
        result = super(GeverBrainSerializer, self).__call__(
            metadata_fields=metadata_fields)

        additional_metadata = set(metadata_fields).intersection(
            self.CONTENTLISTING_METADATA)
        content_listing_obj = IContentListingObject(self.brain)

        for metadata in additional_metadata:
            result[metadata] = getattr(content_listing_obj, metadata)()

        return result
