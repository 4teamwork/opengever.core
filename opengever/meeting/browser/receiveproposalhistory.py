from opengever.base import advancedjson
from opengever.base.request import tracebackify
from opengever.meeting.interfaces import IHistory
from persistent.mapping import PersistentMapping
from Products.Five import BrowserView
from uuid import UUID


@tracebackify
class ReceiveProposalHistory(BrowserView):
    """Receive remote history record data and store locally.

    Receive history from a submitted proposal and store/duplicate it into the
    local proposals history.

    This view is only available for internal requests.
    """

    def __call__(self):
        data = advancedjson.loads(self.request.get('data'))
        timestamp = data['timestamp']

        data = data['data']
        data['uuid'] = UUID(data['uuid'])
        data = PersistentMapping(data)
        IHistory(self.context).receive_record(timestamp, data)

        return 'OK'
