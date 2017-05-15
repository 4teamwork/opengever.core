from ftw.mail.create import CreateMailInContainer
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from opengever.document.interfaces import IDocumentSettings


class OGCreateMailInContainer(CreateMailInContainer):

    def create_mail_object(self, message):
        content = super(OGCreateMailInContainer, self).create_mail_object(
            message)

        content.preserved_as_paper = self.get_preserved_as_paper_default()
        return content

    def get_preserved_as_paper_default(self):
        registry = getUtility(IRegistry)
        document_settings = registry.forInterface(IDocumentSettings)
        return document_settings.preserved_as_paper_default

    def set_defaults(self, obj):
        """Defaults should already set with our patches, so there should be no
        need to do something here."""
        pass
