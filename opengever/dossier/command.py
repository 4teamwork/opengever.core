from opengever.base.command import CreateDocumentCommand
from opengever.dossier.docprops import DocPropertyWriter


class CreateDocumentFromTemplateCommand(CreateDocumentCommand):
    """Store a copy of the template in the new document's primary file field
    """

    skip_defaults_fields = ['title', 'file']

    def __init__(self, context, template_doc, title):
        self.context = context
        self.data = template_doc.file.data
        self.filename = template_doc.file.filename
        self.title = title

    def notify_modified(self, content):
        """Also make sure doc-properties are updated from template."""

        DocPropertyWriter(content).initialize()
        super(CreateDocumentFromTemplateCommand, self).notify_modified(content)
