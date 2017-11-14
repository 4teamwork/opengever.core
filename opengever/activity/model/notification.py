from opengever.base.model import Base
from opengever.ogds.models import USER_ID_LENGTH
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Notification(Base):

    __tablename__ = 'notifications'

    notification_id = Column('id', Integer, Sequence('notifications_id_seq'),
                             primary_key=True)

    userid = Column(String(USER_ID_LENGTH), nullable=False)
    activity_id = Column(Integer, ForeignKey('activities.id'))
    activity = relationship("Activity", backref="notifications")

    is_read = Column(Boolean, default=False, nullable=False)
    is_badge = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return u'<Notification {} for {} on {} >'.format(
            self.notification_id,
            repr(self.userid),
            repr(self.activity.resource))
