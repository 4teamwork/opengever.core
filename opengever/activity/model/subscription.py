from opengever.base.model import Base
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


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
    role = Column(String(100), primary_key=True)

    resource = relationship('Resource', backref="subscriptions")
    watcher = relationship('Watcher', backref="subscriptions")

    def __init__(self, resource=None, watcher=None, role=None):
        self.resource = resource
        self.watcher = watcher
        self.role = role

    def __repr__(self):
        return '<Subscription {!r} @ {!r}>'.format(self.watcher, self.resource)
