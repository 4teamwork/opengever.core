from opengever.base.model import Base
from opengever.base.model import create_session
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class AgendaItem(Base):
    """An item must either have a reference to a proposal or a title.

    """
    __tablename__ = 'agendaitems'

    agenda_item_id = Column("id", Integer, Sequence("agendaitems_id_seq"),
                            primary_key=True)
    proposal_id = Column(Integer, ForeignKey('proposals.id'))
    proposal = relationship("Proposal", uselist=False,
                            backref=backref('agenda_item', uselist=False))

    title = Column(Text)
    number = Column(String(16))
    is_paragraph = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=False, default=0)

    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    meeting = relationship("Meeting")

    discussion = Column(Text)
    decision = Column(Text)

    def update(self, request):
        """Update with changed data."""

        data = request.get(self.name)
        if not data:
            return

        if self.has_proposal:
            self.proposal.legal_basis = data.get('legal_basis')
            self.proposal.initial_position = data.get('initial_position')
            self.proposal.considerations = data.get('considerations')
            self.proposal.proposed_action = data.get('proposed_action')

        self.discussion = data.get('discussion')
        self.decision = data.get('decision')

    def get_field_data(self, include_initial_position=True,
                       include_legal_basis=True, include_considerations=True,
                       include_proposed_action=True, include_discussion=True,
                       include_decision=True):
        data = {
            'number': self.number,
            'description': self.description,
            'title': self.title,
        }
        if include_initial_position:
            data['markdown:initial_position'] = self._sanitize_text(
                self.initial_position)
        if include_legal_basis:
            data['markdown:legal_basis'] = self._sanitize_text(
                self.legal_basis)
        if include_considerations:
            data['markdown:considerations'] = self._sanitize_text(
                self.considerations)
        if include_proposed_action:
            data['markdown:proposed_action'] = self._sanitize_text(
                self.proposed_action)
        if include_discussion:
            data['markdown:discussion'] = self._sanitize_text(self.discussion)
        if include_decision:
            data['markdown:decision'] = self._sanitize_text(self.decision)

        return data

    def _sanitize_text(self, text):
        if not text:
            return None

        return text

    def get_title(self, include_number=False):
        title = self.proposal.title if self.has_proposal else self.title
        if include_number and self.number:
            title = u"{} {}".format(self.number, title)

        return title

    def get_css_class(self):
        return "paragraph" if self.is_paragraph else ""

    def remove(self):
        assert self.meeting.is_editable()

        session = create_session()
        if self.proposal:
            self.proposal.remove_scheduled(self.meeting)
        session.delete(self)
        self.meeting.reorder_agenda_items()

    def get_proposal_link(self, include_icon=True):
        if not self.has_proposal:
            return self.get_title()

        return self.proposal.get_submitted_link(include_icon=include_icon)

    @property
    def has_proposal(self):
        return self.proposal is not None

    @property
    def legal_basis(self):
        return self.proposal.legal_basis if self.has_proposal else None

    @property
    def initial_position(self):
        return self.proposal.initial_position if self.has_proposal else None

    @property
    def considerations(self):
        return self.proposal.considerations if self.has_proposal else None

    @property
    def proposed_action(self):
        return self.proposal.proposed_action if self.has_proposal else None

    @property
    def name(self):
        """Currently used as name for input tags in html."""

        return "agenda_item.{}".format(self.agenda_item_id)

    @property
    def description(self):
        return self.get_title()
