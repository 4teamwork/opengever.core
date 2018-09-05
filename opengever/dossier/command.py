from opengever.base.command import BaseObjectCreatorCommand
from opengever.base.command import CreateDocumentCommand
from opengever.dossier.docprops import DocPropertyWriter
from opengever.dossier.dossiertemplate.dossiertemplate import BEHAVIOR_INTERFACE_MAPPING
from plone.dexterity.utils import iterSchemataForType


class CreateDocumentFromTemplateCommand(CreateDocumentCommand):
    """Store a copy of the template in the new document's primary file field
    """

    def __init__(self, context, template_doc, title, recipient_data=tuple()):
        data = getattr(template_doc.get_file(), "data", None)
        super(CreateDocumentFromTemplateCommand, self).__init__(
            context, template_doc.get_filename(), data,
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
        kw = self._get_additional_attributes(template)
        self.fields = kw["IOpenGeverBase"]
        del kw["IOpenGeverBase"]
        self.additional_fields = kw
        super(CreateDossierFromTemplateCommand, self).__init__(
            context, **self.fields)

    def execute(self):
        obj = super(CreateDossierFromTemplateCommand, self).execute()
        schemas = iterSchemataForType(self.portal_type)
        for schema in schemas:
            schema_name = BEHAVIOR_INTERFACE_MAPPING.get(
                schema.getName(), schema.getName())
            if schema_name not in self.additional_fields:
                continue
            behavior = schema(obj)
            for prop_name in self.additional_fields[schema_name]:
                setattr(behavior, prop_name,
                        self.additional_fields[schema_name][prop_name])
        return obj

    def _get_additional_attributes(self, template):
        """Get all templatable attributes defined in the template.
        """
        kw = template.get_schema_values()
        fields = {}
        for key, value in kw.items():
            schema_name, prop_name = key.split(".")
            if schema_name not in fields:
                fields[schema_name] = {}
            fields[schema_name][prop_name] = value
        return fields
