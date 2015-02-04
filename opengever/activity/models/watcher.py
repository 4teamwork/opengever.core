from opengever.ogds.models import BASE
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


class WatcherQuery(BaseQuery):

    def get_by_userid(self, user_id):
        return self.filter_by(user_id=user_id).first()


class Watcher(BASE):
    """A user
    """
    query_cls = WatcherQuery

    __tablename__ = 'watchers'

    watcher_id = Column('id', Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)
    mail_notification = Column(Boolean(), nullable=False, default=False)

    def __repr__(self):
        return '<Watcher {}>'.format(self.user_id)

    # def active_notification_types(self):
    #     return
