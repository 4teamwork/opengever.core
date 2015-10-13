from opengever.activity.model.subscription import Subscription
from opengever.base.model import Base
from opengever.ogds.models import USER_ID_LENGTH
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class NotificationQuery(BaseQuery):

    def by_user(self, userid):
        return self.filter_by(userid=userid)

    def by_subscription_roles(self, roles, activity):
        subscriptions = Subscription.query.by_resource_and_role(
            activity.resource, roles)
        user_ids = []
        for subscription in subscriptions:
            user_ids += subscription.watcher.get_user_ids()

        return self.filter_by(activity_id=activity.id).filter(
            Notification.userid.in_(user_ids))


class Notification(Base):

    query_cls = NotificationQuery

    __tablename__ = 'notifications'

    notification_id = Column('id', Integer, Sequence('notifications_id_seq'),
                             primary_key=True)

    userid = Column(String(USER_ID_LENGTH), nullable=False)
    activity_id = Column(Integer, ForeignKey('activities.id'))
    activity = relationship("Activity", backref="notifications")

    is_read = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return u'<Notification {} for {} on {} >'.format(
            self.notification_id,
            repr(self.userid),
            repr(self.activity.resource))
