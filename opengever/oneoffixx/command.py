from opengever.base.command import BaseObjectCreatorCommand
from zope.annotation.interfaces import IAnnotations


class CreateDocumentFromOneOffixxTemplateCommand(BaseObjectCreatorCommand):
    """Store a copy of the template in the new document's primary file field
    """

    portal_type = 'opengever.document.document'
    primary_field_name = 'file'

    def __init__(self, context, title, template):
        self.template_id = template.template_id
        self.filename = template.filename
        self.languages = template.languages
        self.content_type = template.content_type
        super(CreateDocumentFromOneOffixxTemplateCommand, self).__init__(
            context, title)

    def execute(self):
        obj = super(CreateDocumentFromOneOffixxTemplateCommand, self).execute()
        annotations = IAnnotations(obj)
        annotations["template-id"] = self.template_id
        annotations["languages"] = self.languages
        annotations["filename"] = self.filename
        annotations["content-type"] = self.content_type

        return obj.as_shadow_document()
