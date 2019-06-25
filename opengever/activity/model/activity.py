from opengever.activity.model.notification import Notification
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import Base
from opengever.base.model import DEFAULT_LOCALE
from opengever.base.model import SUPPORTED_LOCALES
from opengever.base.model import USER_ID_LENGTH
from opengever.base.model import UTCDateTime
from opengever.base.types import UnicodeCoercingText
from opengever.ogds.models.user import User
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from sqlalchemy_i18n import Translatable
from sqlalchemy_i18n import translation_base


class Activity(Base, Translatable):

    __tablename__ = 'activities'
    __translatable__ = {'locales': SUPPORTED_LOCALES,
                        'fallback_locale': DEFAULT_LOCALE}

    locale = DEFAULT_LOCALE

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
        For the activity's actor, who has created the activity, a notification
        is usually unnecessary or disruptive. We therefore only create a
        notification for the activity's actor if he has enabled the
        notify_own_actions'setting.
        """

        notifications = []
        for userid in self.get_users_for_watchers():
            if (self.is_current_user(userid) and not
                    self.user_wants_own_action_notifications(userid)):
                continue

            notifications.append(
                Notification(userid=userid, activity=self))

        return notifications

    def get_users_for_watchers(self):
        users = []
        for watcher in self.resource.watchers:
            users += watcher.get_user_ids()

        return set(users)

    def get_notifications_for_watcher_roles(self, roles):
        """Returns a list of activities notifications, but only those
        where the watchers watch the resource in one of the given roles.
        """
        return Notification.query.by_subscription_roles(roles, self).all()

    def is_current_user(self, user_id):
        return user_id == self.actor_id

    def user_wants_own_action_notifications(self, userid):
        user = User.query.filter_by(userid=userid).one()
        return user.notify_own_actions


class ActivityTranslation(translation_base(Activity)):

    __tablename__ = 'activities_translation'

    title = Column(UnicodeCoercingText)
    label = Column(UnicodeCoercingText)
    summary = Column(UnicodeCoercingText)
    description = Column(UnicodeCoercingText)
