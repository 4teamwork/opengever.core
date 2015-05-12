from opengever.base.model import Base
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


class NotificationDefaultQuery(BaseQuery):

    def is_dispatch_needed(self, dispatch_setting, kind):
        setting = self.filter_by(kind=kind).first()
        if not setting:
            return False

        return getattr(setting, dispatch_setting, False)

    def by_kind(self, kind):
        return self.filter_by(kind=kind)


class NotificationDefault(Base):

    query_cls = NotificationDefaultQuery

    __tablename__ = 'notification_defaults'

    notification_default_id = Column('id', Integer, primary_key=True)

    kind = Column(String(50), nullable=False, unique=True)
    mail_notification = Column(Boolean, nullable=False, default=False)
