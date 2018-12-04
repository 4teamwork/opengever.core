from opengever.base.model import Base
from opengever.base.model import USER_ID_LENGTH
from plone.restapi.serializer.converters import json_compatible
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
    is_digest = Column(Boolean, default=False, nullable=False)

    # Flag if the notification has already been part of a digest mail
    sent_in_digest = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return u'<Notification {} for {} on {} >'.format(
            self.notification_id,
            repr(self.userid),
            repr(self.activity.resource))

    def serialize(self, portal_url):
        return {
            '@id': self._api_url(portal_url),
            'notification_id': self.notification_id,
            'created': json_compatible(self.activity.created),
            'read': self.is_read,
            'title': self.activity.title,
            'label': self.activity.label,
            'link': self._resolve_notification_link(portal_url),
            'summary': self.activity.summary,
        }

    def _resolve_notification_link(self, portal_url):
        return '{}/@@resolve_notification?notification_id={}'.format(
            portal_url, self.notification_id)

    def _api_url(self, portal_url):
        return '{}/@notifications/{}/{}'.format(
            portal_url, self.userid, self.notification_id)
