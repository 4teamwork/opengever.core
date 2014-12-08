from opengever.core.model import create_session
from opengever.meeting.model import Committee


def meeting_service():
    return MeetingService(create_session())


class MeetingService(object):

    def __init__(self, session):
        self.session = session

    def _query_committee(self):
        return self.session.query(Committee)

    def all_committees(self):
        return self._query_committee().all()

    def fetch_committee(self, committee_id):
        return self._query_committee().get(committee_id)
