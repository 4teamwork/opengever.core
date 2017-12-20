from opengever.base.sequence import DefaultSequenceNumberGenerator
from opengever.dossier.behaviors.dossier import IDossierMarker
from zope.component import adapter


@adapter(IDossierMarker)
class DossierSequenceNumberGenerator(DefaultSequenceNumberGenerator):
    """ All dossier-types should use the same range/key of sequence numbers.
    """

    key = 'DossierSequenceNumberGenerator'
