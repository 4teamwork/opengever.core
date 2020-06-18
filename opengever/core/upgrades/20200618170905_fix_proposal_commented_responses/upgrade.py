from ftw.upgrade import UpgradeStep
from opengever.base.response import IResponseContainer
from opengever.base.response import COMMENT_RESPONSE_TYPE
from opengever.meeting.proposal import IBaseProposal


class FixProposalCommentedResponses(UpgradeStep):
    """Fix proposal commented responses.
    """

    deferrable = True

    def __call__(self):
        for proposal in self.objects(
                {'object_provides': IBaseProposal.__identifier__},
                'Migrate proposal history to proposal responses.'):
            self.fix_commented_responses(proposal)

    def fix_commented_responses(self, proposal):
        for response in IResponseContainer(proposal):
            if response.response_type == u'commented':
                response.response_type = COMMENT_RESPONSE_TYPE
