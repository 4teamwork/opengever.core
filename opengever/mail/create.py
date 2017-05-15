from ftw.mail.create import CreateMailInContainer
from opengever.base.command import CreateEmailCommand
from opengever.document.interfaces import IDocumentSettings
from plone import api


class OGCreateMailInContainer(CreateMailInContainer):
    """This adapter is called form ftw.mail when creating mailed-in mails.

    We override it and create mail with `CreateEmailCommand` to make sure
    that creating content programmatically always uses the same code-path.

    """
    def create_mail(self, message):
        """Use `CreateEmailCommand` to create the mailed-in mail."""

        self.check_permission()
        self.check_addable_types()

        command = CreateEmailCommand(
            self.context, 'message.eml', message,
            preserved_as_paper=self.get_preserved_as_paper_default())
        return command.execute()

    def get_preserved_as_paper_default(self):
        return api.portal.get_registry_record(
            'preserved_as_paper_default', interface=IDocumentSettings)
