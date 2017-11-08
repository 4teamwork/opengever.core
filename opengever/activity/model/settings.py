from opengever.base.model import Base
from opengever.ogds.models import USER_ID_LENGTH
from opengever.ogds.models.user import User  # noqa
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
import json


class SettingMixin(object):

    _badge_notification_roles = Column('badge_notification_roles', Text)
    _mail_notification_roles = Column('mail_notification_roles', Text)

    def __init__(self, kind, mail_notification_roles=[],
                 badge_notification_roles=[]):
        self.kind = kind
        self.set_mail_notification_roles(mail_notification_roles)
        self.set_badge_notification_roles(badge_notification_roles)

    @property
    def mail_notification_roles(self):
        return frozenset(json.loads(self._mail_notification_roles))

    def set_mail_notification_roles(self, roles):
        self._mail_notification_roles = json.dumps(roles)

    @property
    def badge_notification_roles(self):
        return frozenset(json.loads(self._badge_notification_roles))

    def set_badge_notification_roles(self, roles):
        self._badge_notification_roles = json.dumps(roles)


class NotificationDefault(SettingMixin, Base):

    __tablename__ = 'notification_defaults'

    notification_default_id = Column('id', Integer,
                                     Sequence('notification_defaults_id_seq'),
                                     primary_key=True)
    kind = Column(String(50), nullable=False, unique=True)

    def __init__(self, kind, mail_notification_roles=[],
                 badge_notification_roles=[]):
        self.kind = kind
        self.set_mail_notification_roles(mail_notification_roles)
        self.set_badge_notification_roles(badge_notification_roles)


class NotificationSetting(SettingMixin, Base):

    __tablename__ = 'notification_settings'

    notification_settings_id = Column('id', Integer,
                                      Sequence('notification_settings_id_seq'),
                                      primary_key=True)

    kind = Column(String(50), nullable=False)
    userid = Column(String(USER_ID_LENGTH), ForeignKey(User.userid))
    user = relationship(User, backref="settings")

    def __init__(self, kind, userid, mail_notification_roles=[],
                 badge_notification_roles=[]):
        self.kind = kind
        self.userid = userid
        self.set_mail_notification_roles(mail_notification_roles)
        self.set_badge_notification_roles(badge_notification_roles)
