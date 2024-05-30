from opengever.base.command import BaseObjectCreatorCommand
from zope.annotation.interfaces import IAnnotations


class CreateDocumentFromOneOffixxTemplateCommand(BaseObjectCreatorCommand):
    """Store a copy of the template in the new document's primary file field
    """

    portal_type = 'opengever.document.document'
    primary_field_name = 'file'

    def execute(self):
        obj = super(CreateDocumentFromOneOffixxTemplateCommand, self).execute()

        # XXX Temporarily pass a *.docx filename to oneoffixx to support at
        # least word templates. Before Office Connector no longer needs a
        # filename and we support all kind of templates.
        annotations = IAnnotations(obj)
        annotations["filename"] = 'oneoffixx_from_template.docx'

        return obj.as_shadow_document()
