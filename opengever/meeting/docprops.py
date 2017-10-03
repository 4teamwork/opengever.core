from opengever.dossier.interfaces import IDocPropertyProvider
from opengever.meeting.proposal import IProposal
from zope.component import adapter
from zope.interface import implementer


@implementer(IDocPropertyProvider)
@adapter(IProposal)
class ProposalDocPropertyProvider(object):

    def __init__(self, context):
        self.context = context

    def get_properties(self):
        proposal_model = self.context.load_model()
        return {
            'ogg.meeting.decision_number': proposal_model.get_decision_number() or '',
        }
