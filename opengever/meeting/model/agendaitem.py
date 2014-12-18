from opengever.core.model import Base
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class AgendaItem(Base):
    """It item must either have a reference to a proposal or a title.

    """

    __tablename__ = 'agendaitems'

    agenda_item_id = Column("id", Integer, Sequence("agendaitems_id_seq"),
                            primary_key=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    meeting = relationship("Meeting", backref='agenda_items')

    proposal_id = Column(Integer, ForeignKey('proposal.id'))
    proposal = relationship("Proposal", backref='agenda_item', uselist=False)

    title = Column(Text)
    sort_order = Column(Integer, nullable=False, default=0)

    def get_title(self):
        return self.proposal.title if self.proposal else self.title
