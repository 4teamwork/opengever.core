from opengever.document.document import Document
from opengever.document.document import IDocumentSchema
from opengever.meeting import _
from os.path import join
from plone.namedfile.field import NamedBlobFile


class ISablonTemplate(IDocumentSchema):

    file = NamedBlobFile(
        title=_(u'label_sablon_template_file', default='File'),
        required=True,
        )


class SablonTemplate(Document):

    def is_movable(self):
        return False

    def is_submitted_document(self):
        return False

    def as_file(self, path):
        """Store template-file data in a file named 'template.doxc' on the
        filesystem under path.

        It is the caller's responsibility to remove the file when it is not
        needed any more.

        Return the file's path.

        """
        file_path = join(path, 'template.docx')
        with open(file_path, 'wb') as template_file:
            template_file.write(self.file.data)
        return file_path
