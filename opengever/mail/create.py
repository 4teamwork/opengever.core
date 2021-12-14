from ftw.mail.create import CreateMailInContainer
from opengever.base.command import CreateEmailCommand
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.mail.mail import MESSAGE_SOURCE_MAILIN
from opengever.propertysheets.creation_defaults import initialize_customproperties_defaults
import email


class OGCreateMailInContainer(CreateMailInContainer):
    """This adapter is called form ftw.mail when creating mailed-in mails.

    We override it and create mail with `CreateEmailCommand` to make sure
    that creating content programmatically always uses the same code-path.

    """
    def create_mail(self, message):
        """Use `CreateEmailCommand` to create the mailed-in mail."""

        self.check_permission()
        self.check_addable_types()

        # we don't set the content-type directly here but choose it with a
        # roundtrip via mimetype registry.
        if self.is_application_pkcs7_mime(message):
            filename = 'message.p7m'
        else:
            filename = 'message.eml'

        command = CreateEmailCommand(self.context, filename, message,
                                     message_source=MESSAGE_SOURCE_MAILIN)

        obj = command.execute()

        # Initialize custom properties with default values
        initialize_customproperties_defaults(obj)

        return obj

    def is_application_pkcs7_mime(self, message_raw):
        """Return if message is of application/pkcs7-mime media type.

        As specified by https://tools.ietf.org/html/rfc8551#section-3.5.3.2.
        """
        message = email.message_from_string(message_raw)
        content_type = message.get_content_type()
        protocol = message.get_param('protocol')

        return (
            content_type == 'multipart/signed'
            and protocol == 'application/x-pkcs7-signature'
        )
