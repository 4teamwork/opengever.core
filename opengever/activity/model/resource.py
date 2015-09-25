from opengever.activity.model.watcher import Watcher
from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.ogds.models import UNIT_ID_LENGTH
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
import json


class WatchingQuery(BaseQuery):

    def get_by_watcher_resource(self, resource, watcher):
        return self.filter_by(resource=resource, watcher=watcher).first()


class Watching(Base):
    query_cls = WatchingQuery
    __tablename__ = 'watchings'
    __table_args__ = (PrimaryKeyConstraint('resource_id', 'watcher_id'),)

    resource_id = Column(Integer, ForeignKey('resources.id'))
    watcher_id = Column(Integer, ForeignKey('watchers.id'))
    _roles = Column('roles', Text)

    resource = relationship('Resource', backref="watchings")
    watcher = relationship('Watcher', backref="watchings")

    def __init__(self, resource=None, watcher=None, roles=[]):
        self.resource = resource
        self.watcher = watcher
        self.roles = roles

    def __repr__(self):
        return '<Watching {!r} @ {!r}>'.format(self.watcher, self.resource)

    @property
    def roles(self):
        return json.loads(self._roles)

    @roles.setter
    def roles(self, roles):
        self._roles = json.dumps(roles)

    def add_role(self, role):
        roles = self.roles
        if role not in roles:
            roles.append(role)

        self.roles = roles

    def remove_role(self, role):
        roles = self.roles
        if role in roles:
            roles.remove(role)
            self.roles = roles


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

    watchers = association_proxy('watchings', 'watcher')

    def __repr__(self):
        return '<Resource {}:{}>'.format(self.admin_unit_id, self.int_id)

    def add_watcher(self, user_id, role):
        watcher = Watcher.query.get_by_userid(user_id)
        if not watcher:
            watcher = Watcher(user_id=user_id)
            create_session().add(watcher)

        watching = Watching.query.get_by_watcher_resource(self, watcher)
        if not watching:
            watching = Watching(resource=self, watcher=watcher, roles=[role])
            create_session().add(watching)
        else:
            watching.add_role(role)

        return watcher

    def remove_watcher(self, watcher):
        self.watchers.remove(watcher)
