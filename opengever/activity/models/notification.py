from opengever.base.model import Base
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship


class NotificationQuery(BaseQuery):

    def by_user(self, userid):
        return self.join(Notification.watcher).filter_by(user_id=userid)


class Notification(Base):

    query_cls = NotificationQuery

    __tablename__ = 'notifications'

    notification_id = Column('id', Integer, primary_key=True)

    watcher_id = Column(Integer, ForeignKey('watchers.id'))
    watcher = relationship("Watcher", backref="notifications")

    activiy_id = Column(Integer, ForeignKey('activities.id'))
    activity = relationship("Activity", backref="notifications")

    read = Column(Boolean(), default=False, nullable=False)

    def __repr__(self):
        return '<Notification {}>'.format(self.notification_id)
