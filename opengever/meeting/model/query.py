from datetime import date
from datetime import datetime
from opengever.base.oguid import Oguid
from opengever.ogds.models.query import BaseQuery
from plone import api
from sqlalchemy import and_
from sqlalchemy import desc
from sqlalchemy import or_


class ProposalQuery(BaseQuery):

    def get_by_oguid(self, oguid):
        """Return the proposal identified by the given oguid or None if no
        such proposal exists.

        """
        return self.filter(self._attribute('oguid') == oguid).first()

    def by_container(self, container, admin_unit):
        # XXX same as TaskQuery
        url_tool = api.portal.get_tool(name='portal_url')
        path = '/'.join(url_tool.getRelativeContentPath(container))

        return self.by_admin_unit(admin_unit)\
                   .filter(self._attribute('physical_path').like(path + '%'))

    def by_admin_unit(self, admin_unit):
        """List all proposals for admin_unit."""

        return self.filter(self._attribute('admin_unit_id') == admin_unit.id())

    def visible_for_committee(self, committee):
        states = ['submitted', 'scheduled']
        query = self.filter(self._attribute('workflow_state').in_(states))
        return query.filter(self._attribute('committee') == committee)


class CommitteeQuery(BaseQuery):

    searchable_fields = ['title']

    def get_by_oguid(self, oguid):
        """Return the committee identified by the given int_id and
        admin_unit_id or None if no such committee exists.

        """
        return self.filter(self._attribute('oguid') == oguid).first()


class MembershipQuery(BaseQuery):

    def only_active(self):
        return self.filter(
            and_(self._attribute('date_from') <= date.today(),
                 self._attribute('date_to') >= date.today()))

    def overlapping(self, start, end):
        return self.filter(and_(self._attribute('date_from') <= end,
                                self._attribute('date_to') >= start))


class SubmittedDocumentQuery(BaseQuery):

    def get_by_source(self, proposal, document):
        oguid = Oguid.for_object(document)
        proposal_model = proposal.load_model()
        return self.filter(self._attribute('oguid') == oguid)\
                   .filter(self._attribute('proposal') == proposal_model)\
                   .first()

    def get_by_target(self, document):
        oguid = Oguid.for_object(document)
        return self.filter(self._attribute('submitted_oguid') == oguid).first()

    def by_document(self, document):
        """Filter by document's oguid on source or target side of a submitted
        doucment.

        """
        oguid = Oguid.for_object(document)
        return self.filter(or_(
            self._attribute('submitted_oguid') == oguid,
            self._attribute('oguid') == oguid
        ))


class MeetingQuery(BaseQuery):

    def _committee_meetings(self, committee):
        return self.filter(self._attribute('committee') == committee)

    def _upcoming_meetings(self, committee):
        query = self._committee_meetings(committee)
        query = query.filter(self._attribute('start') >= datetime.now())
        query = query.order_by(self._attribute('start'))
        return query

    def _past_meetings(self, committee):
        query = self._committee_meetings(committee)
        query = query.filter(self._attribute('start') < datetime.now())
        query = query.order_by(desc(self._attribute('start')))
        return query

    def all_upcoming_meetings(self, committee):
        return self._upcoming_meetings(committee).all()

    def get_next_meeting(self, committee):
        return self._upcoming_meetings(committee).first()

    def get_last_meeting(self, committee):
        return self._past_meetings(committee).first()


class GeneratedDocumentQuery(BaseQuery):

    def by_document(self, document):
        """Filter generated document by document."""

        oguid = Oguid.for_object(document)
        return self.filter(self._attribute('oguid') == oguid)
