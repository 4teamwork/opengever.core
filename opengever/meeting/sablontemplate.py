from opengever.document.document import Document
from opengever.document.document import IDocumentSchema
from opengever.meeting import _
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
