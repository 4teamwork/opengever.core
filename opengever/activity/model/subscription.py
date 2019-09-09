from opengever.base.model import Base
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


class Subscription(Base):
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
