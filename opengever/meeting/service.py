from opengever.base.model import create_session
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Committee
from opengever.meeting.model import Proposal
from sqlalchemy import or_


def meeting_service():
    return MeetingService(create_session())


class MeetingService(object):

    def __init__(self, session):
        self.session = session

    def _query_committee(self):
        return self.session.query(Committee)

    def all_committees(self, text_filter=None):
        query = self._query_committee()
        if text_filter:
            query = self.extend_query_with_textfilter(
                query, text_filter, [Committee.title])

        return query.all()

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

    def extend_query_with_textfilter(self, query, text, fields):
        """Extends the given `query` with text filters. This is only done when
        config's `filter_text` is set.
        """

        if len(text):
            if isinstance(text, str):
                text = text.decode('utf-8')

            # remove trailing asterisk
            if text.endswith('*'):
                text = text[:-1]

            # lets split up the search term into words, extend them with
            # the default wildcards and then search for every word
            # seperately
            for word in text.strip().split(' '):
                term = '%%%s%%' % word
                query = query.filter(
                    or_(*[field.like(term) for field in fields]))

        return query
