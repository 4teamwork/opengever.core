from opengever.base.model import Base
from sqlalchemy import Boolean
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
    mail_notification = Column(Boolean, nullable=False, default=False)
    _mail_notification_roles = Column('mail_notification_roles', Text)

    def __init__(self, kind, mail_notification=False, mail_notification_roles=[]):
        self.kind = kind
        self.mail_notification = mail_notification
        self.set_mail_notification_roles(mail_notification_roles)

    @property
    def mail_notification_roles(self):
        return frozenset(json.loads(self._mail_notification_roles))

    def set_mail_notification_roles(self, roles):
        self._mail_notification_roles = json.dumps(roles)
