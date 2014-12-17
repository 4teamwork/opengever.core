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

    def get_edit_values(self, fieldnames):
        # XXX this should be done in a more generic way by using either
        # the already present valueconverter stuff
        # or by registering our own converters based on column types
        values = {}
        for fieldname in fieldnames:
            value = getattr(self, fieldname, None)
            if not value:
                continue

            if fieldname == 'date':
                values['date-day'] = str(value.day)
                values['date-month'] = str(value.month)
                values['date-year'] = str(value.year)
                continue

            if fieldname in ['start_time', 'end_time']:
                value = value.strftime('%H:%M')
            values[fieldname] = value
        return values

    def update_model(self, data):
        for key, value in data.items():
            setattr(self, key, value)
