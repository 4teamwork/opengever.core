from opengever.activity.model.resource import Resource
from opengever.activity.model.subscription import Subscription
from opengever.base.model import Base
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import and_
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class NotificationQuery(BaseQuery):

    def by_user(self, userid):
        return self.join(Notification.watcher).filter_by(user_id=userid)

    def by_subscription_roles(self, roles, activity):
        query = self.filter_by(activity=activity).join(Notification.activity)
        query = query.join(Resource)
        query = query.join(
            Subscription,
            and_(Resource.resource_id == Subscription.resource_id,
                 Notification.watcher_id == Subscription.watcher_id))
        return query.filter(Subscription.role.in_(roles))


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
