from five import grok
from opengever.base.sequence import DefaultSequenceNumberGenerator
from opengever.base.interfaces import ISequenceNumberGenerator
from opengever.document.behaviors import IBaseDocument

class BaseDocumentSequenceNumberGenerator(DefaultSequenceNumberGenerator):
    """ All dossier-types should use the same range/key of sequence numbers.
    """
    grok.provides(ISequenceNumberGenerator)
    grok.context(IBaseDocument)

    key = 'DefaultSequenceNumberGenerator.opengever.document.document'
