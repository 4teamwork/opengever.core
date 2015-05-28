from opengever.base.model import Base
from opengever.ogds.models import USER_ID_LENGTH
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


class WatcherQuery(BaseQuery):

    def get_by_userid(self, user_id):
        return self.filter_by(user_id=user_id).first()


class Watcher(Base):
    """A user
    """
    query_cls = WatcherQuery

    __tablename__ = 'watchers'

    watcher_id = Column('id', Integer, Sequence('watchers_id_seq'),
                        primary_key=True)
    user_id = Column(String(USER_ID_LENGTH), nullable=False, unique=True)

    def __repr__(self):
        return '<Watcher {}>'.format(repr(self.user_id))
