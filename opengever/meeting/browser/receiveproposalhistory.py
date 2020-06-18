from opengever.base import advancedjson
from opengever.base.request import tracebackify
from opengever.base.response import COMMENT_RESPONSE_TYPE
from opengever.base.response import IResponseContainer
from opengever.base.utils import ok_response
from opengever.meeting.activity.activities import ProposalCommentedActivity
from opengever.meeting.proposalhistory import ProposalResponse
from Products.Five import BrowserView


@tracebackify
class ReceiveProposalHistory(BrowserView):
    """Receive remote history record data and store locally.

    Receive history from a submitted proposal and store/duplicate it into the
    local proposals history.

    This view is only available for internal requests.
    """

    def __call__(self):
        data = advancedjson.loads(self.request.get('data'))
        data = data['data']
        # create response object from data and
        # make sure that response does not get synced back
        response = ProposalResponse.deserialize(data, needs_syncing=False)

        IResponseContainer(self.context).add(response)
        self.generate_activity_if_necessary(response)

        return ok_response(self.request)

    def generate_activity_if_necessary(self, response):
        """When a submitted proposal is commented, we need to generate
        a corresponding activity on the proposal."""
        if response.response_type == COMMENT_RESPONSE_TYPE:
            ProposalCommentedActivity(self.context, self.request).record()
