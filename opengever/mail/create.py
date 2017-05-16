from ftw.mail.create import CreateMailInContainer
from opengever.base.command import CreateEmailCommand


class OGCreateMailInContainer(CreateMailInContainer):
    """This adapter is called form ftw.mail when creating mailed-in mails.

    We override it and create mail with `CreateEmailCommand` to make sure
    that creating content programmatically always uses the same code-path.

    """
    def create_mail(self, message):
        """Use `CreateEmailCommand` to create the mailed-in mail."""

        self.check_permission()
        self.check_addable_types()

        command = CreateEmailCommand(self.context, 'message.eml', message)
        return command.execute()
