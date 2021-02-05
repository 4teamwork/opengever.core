from opengever.base.sequence import DefaultSequenceNumberGenerator
from opengever.document.behaviors import IBaseDocument
from zope.component import adapter


@adapter(IBaseDocument)
class BaseDocumentSequenceNumberGenerator(DefaultSequenceNumberGenerator):
    """ All document-types should use the same range/key of sequence numbers.
    """

    key = 'DefaultSequenceNumberGenerator.opengever.document.document'
