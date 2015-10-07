from opengever.activity.model.watcher import Watcher
from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.ogds.models import UNIT_ID_LENGTH
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from sqlalchemy.types import Enum


TASK_ISSUER_ROLE = 'task_issuer'
TASK_RESPONSIBLE_ROLE = 'task_responsible'
WATCHER_ROLE = 'regular_watcher'


class SubscriptionQuery(BaseQuery):

    def fetch(self, resource, watcher, role):
        return self.filter_by(
            resource=resource, watcher=watcher, role=role).first()

    def get_by_watcher_resource(self, resource, watcher):
        return self.filter_by(resource=resource, watcher=watcher).first()


class Subscription(Base):
    query_cls = SubscriptionQuery
    __tablename__ = 'subscriptions'

    resource_id = Column(Integer, ForeignKey('resources.id'), primary_key=True)
    watcher_id = Column(Integer, ForeignKey('watchers.id'), primary_key=True)
    role = Column(Enum(TASK_ISSUER_ROLE,
                       TASK_RESPONSIBLE_ROLE,
                       WATCHER_ROLE,
                       name='subscription_role_type'), primary_key=True)

    resource = relationship('Resource', backref="subscriptions")
    watcher = relationship('Watcher', backref="subscriptions")

    def __init__(self, resource=None, watcher=None, role=None):
        self.resource = resource
        self.watcher = watcher
        self.role = role

    def __repr__(self):
        return '<Subscription {!r} @ {!r}>'.format(self.watcher, self.resource)


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
