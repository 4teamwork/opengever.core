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

    def get_title(self):
        return self.proposal.title if self.proposal else self.title

    def get_css_class(self):
        return "paragraph" if self.is_paragraph else ""

    def remove(self):
        assert self.meeting.is_editable()

        session = create_session()
        if self.proposal:
            self.proposal.remove_scheduled(self.meeting)
        session.delete(self)
        self.meeting.reorder_agenda_items()

    def has_proposal(self):
        return self.proposal is not None

    def get_proposal_link(self, include_icon=True):
        if not self.has_proposal():
            return self.get_title()

        return self.proposal.get_submitted_link(include_icon=include_icon)
