from opengever.activity.model.settings import NotificationDefault
from opengever.base.model import Base
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class NotificationQuery(BaseQuery):

    def by_user(self, userid):
        return self.join(Notification.watcher).filter_by(user_id=userid)


class Notification(Base):

    query_cls = NotificationQuery

    __tablename__ = 'notifications'

    notification_id = Column('id', Integer, Sequence('notifications_id_seq'),
                             primary_key=True)

    watcher_id = Column(Integer, ForeignKey('watchers.id'))
    watcher = relationship("Watcher", backref="notifications")

    activity_id = Column(Integer, ForeignKey('activities.id'))
    activity = relationship("Activity", backref="notifications")

    is_read = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return u'<Notification {} for {} on {} >'.format(
            self.notification_id,
            repr(self.watcher),
            repr(self.activity.resource))

    def dispatch(self, dispatcher):
        if self.is_dispatch_needed(dispatcher):
            dispatcher.dispatch_notification(self)

    def is_dispatch_needed(self, dispatcher):
        """Lookup if the given dispatcher is needed for the given kind.
        """
        return NotificationDefault.query.is_dispatch_needed(
            dispatcher.setting_key, self.activity.kind)
