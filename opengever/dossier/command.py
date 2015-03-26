from opengever.base.command import CreateDocumentCommand
from opengever.dossier.docprops import DocPropertyWriter


class CreateDocumentFromTemplateCommand(CreateDocumentCommand):
    """Store a copy of the template in the new document's primary file field
    """

    skip_defaults_fields = ['title', 'file']

    def __init__(self, context, template_doc, title):
        super(CreateDocumentFromTemplateCommand, self).__init__(
            context, template_doc.file.filename, template_doc.file.data,
            title=title)

    def finish_creation(self, content):
        """Also make sure doc-properties are updated from template."""

        DocPropertyWriter(content).initialize()
        super(CreateDocumentFromTemplateCommand, self).finish_creation(content)
