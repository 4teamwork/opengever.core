from opengever.core.model import Base
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Time
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class AgendaItem(Base):

    __tablename__ = 'agendaitems'

    agenda_item_id = Column("id", Integer, Sequence("agendaitems_id_seq"),
                            primary_key=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    meeting = relationship("Meeting", backref='agenda_items')

    proposal_id = Column(Integer, ForeignKey('proposals.id'))
    proposal = relationship("Proposal", backref='agenda_item', uselist=False)

    title = Column(String(256))
    sort_order = Column(Integer, nullable=False)
