from ftw.bumblebee.dexterity.document import DXBumblebeeDocument
from opengever.document.document import IDocumentSchema
from opengever.document.subscribers import set_digitally_available
from opengever.mail.mail import IOGMailMarker
from zope.component import adapter


@adapter(IDocumentSchema)
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

        # Ensure that digitally_available is up to date, because
        # is_convertable() below relies on it.
        #
        # This is needed because the event handler that updates it also
        # listens to ObjectModified, and we can't control the order in which
        # subscribers for the same event type are executed.
        set_digitally_available(self.context, None)

        return super(DocumentBumblebeeDocument, self)._handle_update(force=force)

    def is_convertable(self):
        return (self.context.digitally_available
                and super(DocumentBumblebeeDocument, self).is_convertable())


@adapter(IOGMailMarker)
class OGMailBumblebeeDocument(DXBumblebeeDocument):
    """Customized bumblebee document adapter for opengever.mail.mail.
    """

    def get_primary_field(self):
        return self.context.get_file()
