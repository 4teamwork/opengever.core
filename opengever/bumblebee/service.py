from ftw.bumblebee.service import BumblebeeServiceV3
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.bumblebee import is_bumblebee_feature_enabled
from plone import api
from zope.component import adapter


@adapter(IOpengeverBaseLayer)
class GeverBumblebeeService(BumblebeeServiceV3):
    """Only converts/stores when the bumblebee feature is enabled."""

    def is_convertable(self, document):
        if not is_bumblebee_feature_enabled():
            return False
        if not document.get_file_extension():
            return False
        return super(GeverBumblebeeService, self).is_convertable(document)

    def get_not_digitally_available_placeholder_image_url(self, format_name=None):
        if format_name and format_name == 'pdf':
            filename = "fallback_not_digitally_available.pdf"
        else:
            filename = "fallback_not_digitally_available.svg"
        return "{}/++resource++opengever.bumblebee.resources/{}".format(
            api.portal.get().absolute_url(), filename)

    def get_representation_url(self, obj, format_name, filename=''):
        """Returns the bumblebee representation url of object.

        Object can be either a brain or a plone content object.

        Bumblebee will return the representation if the object has a checksum.
        The checksum is only available if the object has an attached document.

        If no checksum is available, the representation_url will be none.

        That means, our object is only preserved as paper and we have to return
        a special placeholder image for this documents.
        """
        url = super(GeverBumblebeeService, self).get_representation_url(
            obj, format_name, filename)
        return url or self.get_not_digitally_available_placeholder_image_url(format_name)
