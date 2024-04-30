from opengever.base.command import BaseObjectCreatorCommand


class CreateDocumentFromOneOffixxTemplateCommand(BaseObjectCreatorCommand):
    """Store a copy of the template in the new document's primary file field
    """

    portal_type = 'opengever.document.document'
    primary_field_name = 'file'

    def execute(self):
        obj = super(CreateDocumentFromOneOffixxTemplateCommand, self).execute()
        return obj.as_shadow_document()
