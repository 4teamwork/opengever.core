from opengever.core.model import create_session
from opengever.meeting.model import Commission


def meeting_service():
    return MeetingService(create_session())


class MeetingService(object):

    def __init__(self, session):
        self.session = session

    def _query_commission(self):
        return self.session.query(Commission)

    def all_commissions(self):
        return self._query_commission().all()

    def fetch_commission(self, commission_id):
        return self._query_commission().get(commission_id)
