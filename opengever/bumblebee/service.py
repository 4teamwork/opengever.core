from ftw.bumblebee.service import BumblebeeService
from opengever.bumblebee import is_bumblebee_feature_enabled


class GeverBumblebeeService(BumblebeeService):
    """Only queues conversions when the bumblebee feature is enabled."""

    def queue_conversion(self, queue, version_id=None):
        if not is_bumblebee_feature_enabled():
            return False

        return super(GeverBumblebeeService, self).queue_conversion(
            queue, version_id=version_id)
