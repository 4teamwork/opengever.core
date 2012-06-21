from five import grok
from opengever.base.sequence import DefaultSequenceNumberGenerator
from opengever.base.interfaces import ISequenceNumberGenerator
from opengever.dossier.behaviors.dossier import IDossierMarker


class DossierSequenceNumberGenerator(DefaultSequenceNumberGenerator):
    """ All dossier-types should use the same range/key of sequence numbers.
    """
    grok.provides(ISequenceNumberGenerator)
    grok.context(IDossierMarker)

    key = 'DossierSequenceNumberGenerator'
