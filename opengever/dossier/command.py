from opengever.base.command import BaseObjectCreatorCommand
from opengever.base.command import CreateDocumentCommand
from opengever.base.default_values import get_persisted_values_for_obj
from opengever.dossier.docprops import DocPropertyWriter


class CreateDocumentFromTemplateCommand(CreateDocumentCommand):
    """Store a copy of the template in the new document's primary file field
    """

    def __init__(self, context, template_doc, title, recipient_data=tuple()):
        super(CreateDocumentFromTemplateCommand, self).__init__(
            context, template_doc.file.filename, template_doc.file.data,
            title=title)
        self.recipient_data = recipient_data

    def finish_creation(self, content):
        """Also make sure doc-properties are updated from template."""

        DocPropertyWriter(content, recipient_data=self.recipient_data).initialize()
        super(CreateDocumentFromTemplateCommand, self).finish_creation(content)


class CreateDossierFromTemplateCommand(BaseObjectCreatorCommand):
    """Store a copy of the dossiertemplate with all its attributes.
    """
    portal_type = 'opengever.dossier.businesscasedossier'

    def __init__(self, context, template):
        super(CreateDossierFromTemplateCommand, self).__init__(
            context, template.title, **self._get_additional_attributes(template))

    def _get_additional_attributes(self, template):
        """Extracts the template attributes to use it as additional attributes.
        """
        data = get_persisted_values_for_obj(template)
        del data['title']  # the titel is already given as a parameter
        for key, val in data.items():
            if not val:
                del data[key]  # Remove unused attributes to get the default value

        return data
