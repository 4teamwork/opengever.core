from opengever.base.model import Base
from opengever.base.model import GROUP_ID_LENGTH
from opengever.base.model import GROUP_TITLE_LENGTH
from opengever.base.model import USER_ID_LENGTH
from opengever.base.query import BaseQuery
from opengever.ogds.models.team import Team
from opengever.ogds.models.user import User
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import backref
from sqlalchemy.orm import relation
from sqlalchemy.orm import relationship


# association table
groups_users = Table(
    'groups_users', Base.metadata,
    Column('groupid', String(GROUP_ID_LENGTH),
           ForeignKey('groups.groupid'), primary_key=True),
    Column('userid', String(USER_ID_LENGTH),
           ForeignKey('users.userid'), primary_key=True),
)


class GroupQuery(BaseQuery):

    searchable_fields = ['groupid', 'title']


class Group(Base):
    """Group model, corresponds to a LDAP group
    """

    query_cls = GroupQuery

    __tablename__ = 'groups'

    groupid = Column(String(GROUP_ID_LENGTH), primary_key=True)
    active = Column(Boolean, default=True)
    title = Column(String(GROUP_TITLE_LENGTH))

    # is_local is set for groups created over the @groups endpoint
    # which should always be plone groups and are the only groups
    # allowed to be managed over the @groups endpoint.
    is_local = Column(Boolean, default=False, nullable=True)

    users = relation(User, secondary=groups_users,
                     backref=backref('groups', order_by='Group.groupid'))
    teams = relationship(Team, back_populates="group")

    column_names_to_sync = {'groupid', 'active', 'title'}

    # A classmethod property needs to be defined on the metaclass
    class __metaclass__(type(Base)):
        @property
        def columns_to_sync(cls):
            return {
                col for col in cls.__table__.columns
                if col.name in cls.column_names_to_sync
            }

    def __init__(self, groupid, **kwargs):
        self.groupid = groupid
        super(Group, self).__init__(**kwargs)

    def __repr__(self):
        return '<Group %s>' % self.groupid

    def __eq__(self, other):
        if isinstance(other, Group):
            return self.groupid == other.groupid
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def id(self):
        return self.groupid

    def label(self):
        return self.title or self.groupid
