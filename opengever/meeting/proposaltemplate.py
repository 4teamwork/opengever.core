from opengever.document.document import Document
from opengever.document.document import IDocumentSchema
from opengever.meeting import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from plone.namedfile.field import NamedBlobFile
from z3c.form.validator import SimpleFieldValidator
from z3c.form.validator import WidgetValidatorDiscriminators
from zope.interface import Invalid
from zope.interface import provider
import os.path


@provider(IFormFieldProvider)
class IProposalTemplate(IDocumentSchema):

    model.primary('file')
    file = NamedBlobFile(
        title=_(u'label_file', default='File'),
        required=True)


class UploadValidator(SimpleFieldValidator):

    allowed_extensions = ('.docx',)

    def validate(self, value):
        """The uploaded file in a proposal template must be a .docx
        so that we can process it later.
        """
        if value and value.filename:
            basename, extension = os.path.splitext(value.filename)
            if extension.lower() in self.allowed_extensions:
                return

        raise Invalid(_(u'error_prosal_template_not_docx',
                        default=u'Only word files (.docx) can be added here.'))


WidgetValidatorDiscriminators(
    UploadValidator,
    field=IProposalTemplate['file'])


class ProposalTemplate(Document):
    """Proposal templates are added to the template folder.
    They have a word-file attached, which is copied when creating a new proposal.
    """

    def is_movable(self):
        return False
