from opengever.document.document import Document
from opengever.document.document import IDocumentSchema
from opengever.meeting import _
from opengever.meeting.browser.sablontemplate import SAMPLE_MEETING_DATA
from opengever.meeting.exceptions import SablonProcessingFailed
from opengever.meeting.sablon import Sablon
from os.path import join
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from zope.annotation.interfaces import IAnnotations
import json

VALIDATION_DATA = {
    'meeting': SAMPLE_MEETING_DATA,
    'toc': {'toc': []},
}


def sablon_template_is_valid(value):
    # create the sablon template using the blob file
    sablon = Sablon(None)

    for template_type, data in VALIDATION_DATA.items():
        try:
            sablon.process(json.dumps(data), namedblobfile=value)
            return True
        except SablonProcessingFailed:
            continue
    return False


class ISablonTemplate(IDocumentSchema):

    model.primary('file')
    file = NamedBlobFile(
        title=_(u'label_sablon_template_file', default='File'),
        required=True,
    )


class SablonTemplate(Document):

    def is_movable(self):
        return False

    def is_submitted_document(self):
        return False

    def is_valid_sablon_template(self):
        return IAnnotations(self).get(
            'opengever.meeting.sablon_template_is_valid',
            None)

    def as_file(self, path):
        """Store template-file data in a file named 'template.docx' on the
        filesystem under path.

        It is the caller's responsibility to remove the file when it is not
        needed any more.

        Return the file's path.

        """
        file_path = join(path, 'template.docx')
        with open(file_path, 'wb') as template_file:
            template_file.write(self.file.data)
        return file_path
