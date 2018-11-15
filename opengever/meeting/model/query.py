from datetime import date
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.oguid import Oguid
from opengever.meeting.model.committee import Committee
from opengever.meeting.model.excerpt import Excerpt
from opengever.meeting.model.generateddocument import GeneratedDocument
from opengever.meeting.model.meeting import Meeting
from opengever.meeting.model.membership import Membership
from opengever.meeting.model.period import Period
from opengever.meeting.model.proposal import Proposal
from opengever.meeting.model.submitteddocument import SubmittedDocument
from opengever.base.query import BaseQuery
from plone import api
from sqlalchemy import and_
from sqlalchemy import desc
from sqlalchemy import or_


class ProposalQuery(BaseQuery):

    def get_by_oguid(self, oguid):
        """Return the proposal identified by the given oguid or None if no
        such proposal exists.

        """
        return self.filter(Proposal.oguid == oguid).first()

    def by_container(self, container, admin_unit):
        # XXX same as TaskQuery
        url_tool = api.portal.get_tool(name='portal_url')
        path = '/'.join(url_tool.getRelativeContentPath(container))

        return self.by_admin_unit(admin_unit)\
                   .filter(Proposal.physical_path.like(path + '%'))

    def by_admin_unit(self, admin_unit):
        """List all proposals for admin_unit."""

        return self.filter(Proposal.admin_unit_id == admin_unit.id())

    def visible_for_committee(self, committee):
        query = self.by_states(
            Proposal.STATE_SUBMITTED,
            Proposal.STATE_SCHEDULED,
            Proposal.STATE_DECIDED)
        return query.for_committee(committee)

    def for_committee(self, committee):
        return self.filter(Proposal.committee == committee)

    def active(self):
        return self.by_states(
            Proposal.STATE_PENDING,
            Proposal.STATE_SUBMITTED,
            Proposal.STATE_SCHEDULED)

    def decided(self):
        return self.by_states(Proposal.STATE_DECIDED)

    def by_states(self, *states):
        return self.filter(Proposal.workflow_state.in_(
            [state.name for state in states]))

    def by_issuer(self, issuer_id):
        return self.filter(Proposal.issuer == issuer_id)


Proposal.query_cls = ProposalQuery


class ExcerptQuery(BaseQuery):

    def by_oguid(self, oguid):
        """Return the query for the given oguid
        """
        return self.filter(Excerpt.excerpt_oguid == oguid)


Excerpt.query_cls = ExcerptQuery


class CommitteeQuery(BaseQuery):

    searchable_fields = ['title']

    def get_by_oguid(self, oguid):
        """Return the committee identified by the given int_id and
        admin_unit_id or None if no such committee exists.

        """
        return self.filter(Committee.oguid == oguid).first()

    def active(self):
        return self.filter(
            Committee.workflow_state == Committee.STATE_ACTIVE.name)


Committee.query_cls = CommitteeQuery


class MembershipQuery(BaseQuery):

    def for_meeting(self, meeting):
        """Return all memberships that are active when the meeting takes place.
        """

        start_date = meeting.start.date()
        end_date = start_date
        if meeting.end:
            end_date = meeting.end.date()

        query = self.filter(
            and_(Membership.date_from <= start_date,
                 Membership.date_to >= end_date))
        return query.filter_by(committee=meeting.committee)

    def only_active(self):
        return self.filter(
            and_(Membership.date_from <= date.today(),
                 Membership.date_to >= date.today()))

    def overlapping(self, start, end):
        return self.filter(and_(Membership.date_from <= end,
                                Membership.date_to >= start))

    def fetch_overlapping(self, start, end, member, committee, ignore_id=None):
        query = self.overlapping(start, end)
        query = query.filter_by(member=member)
        query = query.filter_by(committee=committee)
        if ignore_id:
            query = query.filter(Membership.membership_id != ignore_id)

        return query.first()

    def fetch_for_meeting(self, meeting, member):
        """Fetch the membership for a member at the time of a meeting."""

        end = meeting.end if meeting.end else meeting.start
        return self.fetch_overlapping(
            meeting.start, end, member, meeting.committee)


Membership.query_cls = MembershipQuery


class SubmittedDocumentQuery(BaseQuery):

    def get_by_source(self, proposal, document):
        """Get the one submitted document for proposal and document.
        """

        oguid = Oguid.for_object(document)
        proposal_model = proposal.load_model()
        return self.filter(SubmittedDocument.oguid == oguid)\
                   .filter(SubmittedDocument.proposal == proposal_model)\
                   .first()

    def get_by_target(self, document):
        oguid = Oguid.for_object(document)
        return self.filter(SubmittedDocument.submitted_oguid == oguid).first()

    def by_source(self, document):
        """Return all submitted documents where document is on the source
        side.
        """

        oguid = Oguid.for_object(document)
        return self.filter(SubmittedDocument.oguid == oguid)

    def by_document(self, document):
        """Filter by document's oguid on source or target side of a submitted
        doucment.

        """
        oguid = Oguid.for_object(document)
        return self.filter(or_(
            SubmittedDocument.submitted_oguid == oguid,
            SubmittedDocument.oguid == oguid
        ))


SubmittedDocument.query_cls = SubmittedDocumentQuery


class MeetingQuery(BaseQuery):

    def _committee_meetings(self, committee):
        return self.filter(Meeting.committee == committee)

    def _upcoming_meetings(self, committee):
        query = self._committee_meetings(committee)
        query = query.filter(
            Meeting.workflow_state != Meeting.STATE_CANCELLED.name)
        query = query.filter(Meeting.start >= utcnow_tz_aware())
        query = query.order_by(Meeting.start)
        return query

    def _past_meetings(self, committee):
        query = self._committee_meetings(committee)
        query = query.filter(
            Meeting.workflow_state != Meeting.STATE_CANCELLED.name)
        query = query.filter(Meeting.start < utcnow_tz_aware())
        query = query.order_by(Meeting.start.desc())
        return query

    def all_upcoming_meetings(self, committee):
        return self._upcoming_meetings(committee).all()

    def all_closed_meetings(self, committee):
        return self._past_meetings(committee).all()

    def get_next_meeting(self, committee):
        return self._upcoming_meetings(committee).first()

    def get_last_meeting(self, committee):
        return self._past_meetings(committee).first()

    def pending_meetings(self, committee):
        query = self._committee_meetings(committee)
        query = query.filter(Meeting.workflow_state != Meeting.STATE_CLOSED.name)
        query = query.order_by(Meeting.start.desc())
        return query

    def by_dossier(self, dossier):
        dossier_oguid = Oguid.for_object(dossier)
        return self.filter_by(dossier_oguid=dossier_oguid)

    def active(self):
        return self.filter(Meeting.workflow_state.in_(
            [Meeting.STATE_HELD.name, Meeting.STATE_PENDING.name]))


Meeting.query_cls = MeetingQuery


class GeneratedDocumentQuery(BaseQuery):

    def by_document(self, document):
        """Filter generated document by document."""

        oguid = Oguid.for_object(document)
        return self.filter(GeneratedDocument.oguid == oguid)


GeneratedDocument.query_cls = GeneratedDocumentQuery


class PeriodQuery(BaseQuery):

    def active(self):
        return self.filter_by(workflow_state=Period.STATE_ACTIVE.name)

    def by_committee(self, committee):
        return self.filter_by(committee=committee)

    def get_current(self, committee):
        return self.active().by_committee(committee).one()

    def get_current_for_update(self, committee):
        return self.with_for_update().get_current(committee)


Period.query_cls = PeriodQuery
