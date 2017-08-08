from ftw.bumblebee.dexterity.document import DXBumblebeeDocument
from opengever.document.document import IDocumentSchema
from opengever.mail.mail import IOGMail
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

        return super(DocumentBumblebeeDocument, self)._handle_update(force=force)

    def is_convertable(self):
        return (self.context.digitally_available and
                super(DocumentBumblebeeDocument, self).is_convertable())


@adapter(IOGMailMarker)
class OGMailBumblebeeDocument(DXBumblebeeDocument):
    """Customized bumblebee document adapter for opengever.mail.mail.
    """

    def get_primary_field(self):
        """An opengever mail has two fields for storing the mail-data.

        - The primary-field contains the .eml file which is either a converted
          version of a .msg-file or a directly uploaded .eml-file.

        - The original_message-field contains the original .msg-file, but only
          if the user uploaded one. This file will be used to generate the .eml-file
          for the primary-field.

        For the bumblebee-representation we want to use the original_message (.msg)
        if available. Otherwise we just use the default implementation which
        will return the primary-field. In our case, the .eml-file.
        """
        original_message = IOGMail(self.context).original_message
        if original_message:
            return original_message
        return super(OGMailBumblebeeDocument, self).get_primary_field()
