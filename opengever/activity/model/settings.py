from opengever.base.model import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.schema import Sequence
import json


class NotificationDefault(Base):

    __tablename__ = 'notification_defaults'

    notification_default_id = Column('id', Integer,
                                     Sequence('notification_defaults_id_seq'),
                                     primary_key=True)

    kind = Column(String(50), nullable=False, unique=True)

    _badge_notification_roles = Column('badge_notification_roles', Text)

    _mail_notification_roles = Column('mail_notification_roles', Text)

    @property
    def mail_notification_roles(self):
        roles = self._mail_notification_roles
        if roles:
            return frozenset(json.loads(self._mail_notification_roles))

        return frozenset([])

    @mail_notification_roles.setter
    def mail_notification_roles(self, roles):
        self._mail_notification_roles = json.dumps(roles)

    @property
    def badge_notification_roles(self):
        roles = self._badge_notification_roles
        if roles:
            return frozenset(json.loads(self._badge_notification_roles))

        return frozenset([])

    @badge_notification_roles.setter
    def badge_notification_roles(self, roles):
        self._badge_notification_roles = json.dumps(roles)
