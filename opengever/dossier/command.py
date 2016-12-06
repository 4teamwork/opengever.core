from opengever.base.command import BaseObjectCreatorCommand
from opengever.base.command import CreateDocumentCommand
from opengever.dossier.docprops import DocPropertyWriter
from opengever.dossier.dossiertemplate.dossiertemplate import TEMPLATABLE_FIELDS
from plone.dexterity.utils import iterSchemata
from zope.schema import getFieldsInOrder


class CreateDocumentFromTemplateCommand(CreateDocumentCommand):
    """Store a copy of the template in the new document's primary file field
    """

    def __init__(self, context, template_doc, title, recipient_data=tuple()):
        super(CreateDocumentFromTemplateCommand, self).__init__(
            context, template_doc.file.filename, template_doc.file.data,
            title=title)
        self.recipient_data = recipient_data

    def execute(self):
        obj = super(CreateDocumentFromTemplateCommand, self).execute()
        DocPropertyWriter(obj, recipient_data=self.recipient_data).initialize()
        return obj


class CreateDossierFromTemplateCommand(BaseObjectCreatorCommand):
    """Creates a new dossier based on the dossiertemplate.
    """
    portal_type = 'opengever.dossier.businesscasedossier'

    def __init__(self, context, template):
        super(CreateDossierFromTemplateCommand, self).__init__(
            context, **self._get_additional_attributes(template))

    def _get_additional_attributes(self, template):
        """Get all attributes defined in the template.
        """
        data = {}
        for schema in iterSchemata(template):
            fields = getFieldsInOrder(schema)
            for name, field in fields:
                full_name = '{}.{}'.format(schema.__name__, name)
                if full_name not in TEMPLATABLE_FIELDS:
                    continue

                value = field.get(template)
                if not value:
                    continue

                data[name] = value

        return data
