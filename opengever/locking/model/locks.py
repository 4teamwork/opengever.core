from datetime import timedelta
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import Base
from opengever.base.model import USER_ID_LENGTH
from opengever.base.model import UTCDateTime
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.schema import Sequence


DEFAULTTIMEOUT = 12 * 60L


def lowest_valid():
    return utcnow_tz_aware() - timedelta(seconds=DEFAULTTIMEOUT)


class Lock(Base):

    __tablename__ = 'locks'
    __table_args__ = (UniqueConstraint('object_id', 'object_type', 'lock_type'), {})

    lock_id = Column("id", Integer, Sequence("locks_id_seq"), primary_key=True)
    object_id = Column(Integer)
    object_type = Column(String(100), index=True)
    creator = Column(String(USER_ID_LENGTH), index=True)
    time = Column(UTCDateTime(timezone=True), default=utcnow_tz_aware, index=True)
    lock_type = Column(String(100))

    @property
    def token(self):
        return '{}:{}'.format(self.object_type, self.object_id)

    def is_valid(self):
        return self.time >= lowest_valid()
