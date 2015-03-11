from opengever.activity.models.notification import Notification
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models import BASE
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship
import datetime


class ActivityQuery(BaseQuery):

    pass


class Activity(BASE):

    query_cls = ActivityQuery

    __tablename__ = 'activities'

    activity_id = Column('id', Integer, primary_key=True)
    kind = Column(String(50), nullable=False)
    actor_id = Column(String(255), nullable=False)
    title = Column(String(512), nullable=False)
    summary = Column(String(512), nullable=False)
    description = Column(Text)
    created = Column(DateTime, default=datetime.datetime.utcnow)

    resource_id = Column(Integer, ForeignKey('resources.id'), nullable=False)
    resource = relationship("Resource", backref="activities")

    def __init__(self, **kwargs):
        super(Activity, self).__init__(**kwargs)

    def create_notifications(self):
        """Create for every resource watcher the corresponding notification.
        The actor of the activity is ignored.
        """
        notifications = []
        for watcher in self.resource.watchers:
            if not self.is_current_user(watcher):
                notifications.append(
                    Notification(watcher=watcher, activity=self))

        return notifications

    def is_current_user(self, watcher):
        return watcher.user_id == self.actor_id

    def get_link(self):
        return u'{}/resolve_oguid?oguid={}'.format(
            get_current_admin_unit().public_url,
            self.resource.oguid)

    def render_link(self):
        return u'<a href="{}">{}</a>'.format(self.get_link(), self.title)
