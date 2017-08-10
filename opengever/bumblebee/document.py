from ftw.bumblebee.dexterity.document import DXBumblebeeDocument
from opengever.mail.mail import IOGMail


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

    def is_convertable(self):
        return (self.context.digitally_available and
                super(DocumentBumblebeeDocument, self).is_convertable())


class OGMailBumblebeeDocument(DXBumblebeeDocument):
    """Customized bumblebee document adapter for opengever.mail.mail.
    """

    def get_primary_field(self):
        return self.context.get_file()
