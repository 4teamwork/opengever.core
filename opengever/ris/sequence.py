from opengever.base.interfaces import ISequenceNumberGenerator
from opengever.base.sequence import DefaultSequenceNumberGenerator
from opengever.ris import LEGACY_PROPOSAL_TYPE
from opengever.ris.proposal import IProposal
from zope.component import adapter
from zope.interface import implementer


@implementer(ISequenceNumberGenerator)
@adapter(IProposal)
class ProposalSequenceNumberGenerator(DefaultSequenceNumberGenerator):
    """Share sequence numbers with opengever.meeting.proposal"""

    @property
    def key(self):
        return u'DefaultSequenceNumberGenerator.%s' % LEGACY_PROPOSAL_TYPE
