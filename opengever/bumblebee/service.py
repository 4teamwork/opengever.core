from ftw.bumblebee.service import BumblebeeServiceV3
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.document.document import IDocumentSchema


class GeverBumblebeeService(BumblebeeServiceV3):
    """Only queues storings when the bumblebee feature is enabled."""

    def queue_storing(self, document, queue, deferred=False):
        if not is_bumblebee_feature_enabled():
            return False

        return super(GeverBumblebeeService, self).queue_storing(
            document, queue, deferred=deferred)

    def handle_update(self, document, force=False):
        """Do nothing when attempting to update a checked out document.

        This prevents that a preview of a working copy is rendered, it would
        be visible to all the other users as well.
        """
        if IDocumentSchema.providedBy(document):
            if document.is_checked_out():
                return

        return super(GeverBumblebeeService, self).handle_update(document, force=force)
