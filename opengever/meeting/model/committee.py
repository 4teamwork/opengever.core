from datetime import date
from opengever.base.model import Base
from opengever.base.model import GROUP_ID_LENGTH
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.oguid import Oguid
from opengever.base.types import UnicodeCoercingText
from opengever.base.utils import escape_html
from opengever.globalindex.model import WORKFLOW_STATE_LENGTH
from opengever.meeting import _
from opengever.meeting.model import Meeting
from opengever.meeting.model.member import Member
from opengever.meeting.model.membership import Membership
from opengever.meeting.model.proposal import Proposal
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
from opengever.ogds.base.utils import ogds_service
from sqlalchemy import and_
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import composite
from sqlalchemy.orm import joinedload
from sqlalchemy.schema import Sequence


class Committee(Base):

    __tablename__ = 'committees'
    __table_args__ = (UniqueConstraint('admin_unit_id', 'int_id'), {})

    STATE_ACTIVE = State('active', is_default=True,
                         title=_('active', default='Active'))
    STATE_INACTIVE = State('inactive', title=_('inactive', default='Inactive'))

    workflow = Workflow(
        [STATE_ACTIVE, STATE_INACTIVE],
        [Transition(
            'active', 'inactive',
            title=_('label_deactivate', default='Deactivate committee'),
            visible=False),
         Transition(
             'inactive', 'active',
             title=_('label_reactivate', default='Reactivate committee'),
             visible=False)],
    )

    committee_id = Column("id", Integer, Sequence("committee_id_seq"),
                          primary_key=True)

    group_id = Column(String(GROUP_ID_LENGTH),
                      nullable=False)

    admin_unit_id = Column(String(UNIT_ID_LENGTH), nullable=False)
    int_id = Column(Integer, nullable=False)
    oguid = composite(Oguid, admin_unit_id, int_id)
    title = Column(String(256), index=True)
    physical_path = Column(UnicodeCoercingText, nullable=False)
    workflow_state = Column(String(WORKFLOW_STATE_LENGTH),
                            nullable=False,
                            default=workflow.default_state.name)

    def __repr__(self):
        return '<Committee {}>'.format(repr(self.title))

    def is_active(self):
        return self.get_state() == self.STATE_ACTIVE

    def get_admin_unit(self):
        return ogds_service().fetch_admin_unit(self.admin_unit_id)

    def get_link(self):
        url = self.get_url()
        if not url:
            return ''

        link = u'<a href="{0}" title="{1}">{1}</a>'.format(
            url, escape_html(self.title))
        return link

    def get_url(self, admin_unit=None):
        admin_unit = admin_unit or self.get_admin_unit()
        if not admin_unit:
            return None

        return '/'.join((admin_unit.public_url, self.physical_path))

    def get_state(self):
        return self.workflow.get_state(self.workflow_state)

    def resolve_committee(self):
        return self.oguid.resolve_object()

    def get_protocol_header_template(self):
        return self.resolve_committee().get_protocol_header_template()

    def get_protocol_suffix_template(self):
        return self.resolve_committee().get_protocol_suffix_template()

    def get_agenda_item_header_template(self):
        return self.resolve_committee().get_agenda_item_header_template()

    def get_agenda_item_suffix_template(self):
        return self.resolve_committee().get_agenda_item_suffix_template()

    def get_excerpt_header_template(self):
        return self.resolve_committee().get_excerpt_header_template()

    def get_excerpt_suffix_template(self):
        return self.resolve_committee().get_excerpt_suffix_template()

    def get_agendaitem_list_template(self):
        return self.resolve_committee().get_agendaitem_list_template()

    def get_toc_template(self):
        return self.resolve_committee().get_toc_template()

    def get_active_memberships(self):
        return Membership.query.filter_by(
            committee=self).only_active()

    def get_active_members(self):
        return (Member
                .query
                .join(Member.memberships)
                .options(joinedload(Member.memberships))
                .filter(and_(Membership.committee == self,
                             Membership.date_from <= date.today(),
                             Membership.date_to >= date.today()))
                .order_by(Member.lastname))

    def deactivate(self):
        if self.has_pending_meetings() or self.has_unscheduled_proposals():
            return False

        return self.workflow.execute_transition(None, self, 'active-inactive')

    def reactivate(self):
        return self.workflow.execute_transition(None, self, 'inactive-active')

    def check_deactivate_conditions(self):
        conditions = [self.all_meetings_closed,
                      self.no_unscheduled_proposals]

        for condition in conditions:
            if not condition():
                return False

        return True

    def has_pending_meetings(self):
        return bool(Meeting.query.pending_meetings(self).count())

    def has_unscheduled_proposals(self):
        query = Proposal.query.filter_by(
            committee=self, workflow_state=Proposal.STATE_SUBMITTED.name)

        return bool(query.count())
