from opengever.activity.model.subscription import Subscription
from opengever.activity.model.watcher import Watcher
from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.ogds.models import UNIT_ID_LENGTH
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import composite
from sqlalchemy.schema import Sequence


class ResourceQuery(BaseQuery):

    def get_by_oguid(self, oguid):
        return self.filter_by(oguid=oguid).first()


class Resource(Base):

    query_cls = ResourceQuery

    __tablename__ = 'resources'
    __table_args__ = (UniqueConstraint('admin_unit_id', 'int_id'), {})

    resource_id = Column('id', Integer, Sequence('resources_id_seq'),
                         primary_key=True)

    admin_unit_id = Column(String(UNIT_ID_LENGTH), index=True, nullable=False)
    int_id = Column(Integer, index=True, nullable=False)
    oguid = composite(Oguid, admin_unit_id, int_id)

    watchers = association_proxy('subscriptions', 'watcher')

    def __repr__(self):
        return '<Resource {}:{}>'.format(self.admin_unit_id, self.int_id)

    def add_watcher(self, user_id, role):
        watcher = Watcher.query.get_by_userid(user_id)
        if not watcher:
            watcher = Watcher(user_id=user_id)
            create_session().add(watcher)

        subscription = Subscription.query.fetch(self, watcher, role)
        if not subscription:
            subscription = Subscription(
                resource=self, watcher=watcher, role=role)
            create_session().add(subscription)

        return watcher

    def remove_watcher(self, watcher):
        self.watchers.remove(watcher)
