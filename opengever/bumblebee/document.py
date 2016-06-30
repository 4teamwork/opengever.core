from ftw.bumblebee.dexterity.document import DXBumblebeeDocument


class DocumentBumblebeeDocument(DXBumblebeeDocument):
    """Customized bumblebee document adapter for opengever.document.document.

    """
    def _handle_update(self, force=False):
        """Do nothing when attempting to update a checked out document.

        This prevents that a preview of a working copy is rendered, it would
        be visible to all the other users as well.
        """
        if self.context.is_checked_out():
            return

        return super(DocumentBumblebeeDocument, self)._handle_update(force=force)
