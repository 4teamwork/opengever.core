from opengever.core.model import Base
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Time
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Meeting(Base):

    __tablename__ = 'meetings'

    meeting_id = Column("id", Integer, Sequence("meeting_id_seq"),
                         primary_key=True)
    committee_id = Column(Integer, ForeignKey('committees.id'), nullable=False)
    committee = relationship("Committee", backref='meetings')
    location = Column(String(256))
    date = Column(Date, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)

    def __repr__(self):
        return '<Meeting at "{}">'.format(self.date)
