from ftw.bumblebee.service import BumblebeeServiceV3
from opengever.bumblebee import is_bumblebee_feature_enabled


class GeverBumblebeeService(BumblebeeServiceV3):
    """Only queues storings when the bumblebee feature is enabled."""

    def queue_storing(self, queue):
        if not is_bumblebee_feature_enabled():
            return False

        return super(GeverBumblebeeService, self).queue_storing(queue)
