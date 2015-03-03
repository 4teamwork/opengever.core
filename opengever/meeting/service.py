from datetime import date
from opengever.base.model import create_session
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Committee
from opengever.meeting.model import Meeting
from opengever.meeting.model import Proposal
from sqlalchemy import desc


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

    def fetch_proposal_by_oguid(self, proposal_oguid):
        return Proposal.query.get_by_oguid(proposal_oguid)

    def get_submitted_proposals(self, committee):
        return Proposal.query.filter_by(committee=committee,
                                        workflow_state='submitted').all()

    def fetch_proposal(self, proposal_id):
        return Proposal.get(proposal_id)

    def fetch_agenda_item(self, agenda_item_id):
        return AgendaItem.query.get(agenda_item_id)

    def get_upcoming_meetings(self, committee):
        query = Meeting.query.filter_by(committee=committee)
        query = query.filter(Meeting.date >= date.today())

        return query.all()

    def get_next_meeting(self, committee):
        query = Meeting.query.filter_by(committee=committee)
        query = query.filter(Meeting.date >= date.today())
        query = query.order_by(Meeting.date)
        return query.first()

    def get_last_meeting(self, committee):
        query = Meeting.query.filter_by(committee=committee)
        query = query.filter(Meeting.date < date.today())
        query = query.order_by(desc(Meeting.date))
        return query.first()
