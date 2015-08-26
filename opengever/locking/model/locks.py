from datetime import datetime
from datetime import timedelta
from opengever.base.model import Base
from opengever.base.model import UTCDateTime
from opengever.ogds.models import USER_ID_LENGTH
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.schema import Sequence
import pytz


DEFAULTTIMEOUT = 12 * 60L


def utcnow_tz_aware():
    """Returns the utc now datetime timezone aware."""
    return datetime.now(pytz.utc)


def lowest_valid():
    return utcnow_tz_aware() - timedelta(seconds=DEFAULTTIMEOUT)


class LockQuery(BaseQuery):

    def valid_locks(self, object_type, object_id):
        query = Lock.query.filter_by(object_type=object_type,
                                     object_id=object_id)
        return query.filter(Lock.time >= lowest_valid())

    def invalid_locks(self):
        return Lock.query.filter(Lock.time < lowest_valid())


class Lock(Base):

    __tablename__ = 'locks'
    __table_args__ = (UniqueConstraint('object_id', 'object_type', 'lock_type'), {})

    query_cls = LockQuery

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
