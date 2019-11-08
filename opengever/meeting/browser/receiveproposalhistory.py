from opengever.base import advancedjson
from opengever.base.request import tracebackify
from opengever.base.utils import ok_response
from Products.Five import BrowserView
from opengever.base.response import IResponseContainer
from opengever.meeting.proposalhistory import ProposalResponse


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
        response = ProposalResponse()
        response.deserialize(data)

        # make sure that response does not get synced back
        response._needs_syncing = False

        IResponseContainer(self.context).add(response)

        return ok_response(self.request)
