from opengever.activity.model.notification import Notification
from opengever.base.model import Base
from opengever.base.model import UTCDateTime
from opengever.ogds.models import USER_ID_LENGTH
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from sqlalchemy_i18n import Translatable, translation_base
import datetime
import pytz


def utcnow_tz_aware():
    """Returns the utc now datetime timezone aware."""
    return datetime.datetime.now(pytz.utc)


class ActivityQuery(BaseQuery):
    pass


class Activity(Base, Translatable):

    query_cls = ActivityQuery

    __tablename__ = 'activities'
    __translatable__ = {'locales': ['de', 'fr']}

    locale = 'de'

    id = Column('id', Integer, Sequence("activities_id_seq"),
                         primary_key=True)
    kind = Column(String(255), nullable=False)
    actor_id = Column(String(USER_ID_LENGTH), nullable=False)
    created = Column(UTCDateTime(timezone=True), default=utcnow_tz_aware)
    resource_id = Column(Integer, ForeignKey('resources.id'), nullable=False)
    resource = relationship("Resource", backref="activities")

    def __repr__(self):
        return u'<Activity {} on {} >'.format(self.kind, repr(self.resource))

    def create_notifications(self):
        """Create a notification for every resource watcher.
        Don't create a notification for the activity's actor, he had create the
        activity, therefore a notification is unecessary or disruptive.
        """

        notifications = []
        for watcher in self.resource.watchers:
            if not self.is_current_user(watcher):
                notifications.append(
                    Notification(watcher=watcher, activity=self))

        return notifications

    def is_current_user(self, watcher):
        return watcher.user_id == self.actor_id


class ActivityTranslation(translation_base(Activity)):

    __tablename__ = 'activities_translation'

    title = Column(String(512), nullable=False)
    label = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    description = Column(Text)
