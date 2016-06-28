from ftw.bumblebee.service import BumblebeeServiceV3
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.document.document import IDocumentSchema
from plone import api


class GeverBumblebeeService(BumblebeeServiceV3):
    """Only queues storings when the bumblebee feature is enabled."""

    def queue_storing(self, document, queue, deferred=False):
        if not is_bumblebee_feature_enabled():
            return False

        return super(GeverBumblebeeService, self).queue_storing(
            document, queue, deferred=deferred)


    def get_not_digitally_available_placeholder_image_url(self):
        return "{}{}".format(
            api.portal.get().absolute_url(),
            "/++resource++opengever.bumblebee.resources/fallback_not_digitally_available.png")

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
        return url or self.get_not_digitally_available_placeholder_image_url()
