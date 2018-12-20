from opengever.activity.model.subscription import Subscription
from opengever.activity.model.watcher import Watcher
from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.oguid import Oguid
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import composite
from sqlalchemy.schema import Sequence


class Resource(Base):

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

    def add_watcher(self, actorid, role):
        watcher = Watcher.query.get_by_actorid(actorid)
        if not watcher:
            watcher = Watcher(actorid=actorid)
            create_session().add(watcher)

        subscription = Subscription.query.fetch(self, watcher, role)
        if not subscription:
            subscription = Subscription(
                resource=self, watcher=watcher, role=role)
            create_session().add(subscription)

        return watcher

    def remove_watcher(self, watcher):
        self.watchers.remove(watcher)
