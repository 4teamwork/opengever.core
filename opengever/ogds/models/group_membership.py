from opengever.base.model import Base
from opengever.base.model import GROUP_ID_LENGTH
from opengever.base.model import USER_ID_LENGTH
from sqlalchemy import Column
from sqlalchemy import event
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship


class GroupMembership(Base):

    __tablename__ = "groups_users"

    groupid = Column(String(GROUP_ID_LENGTH),
                     ForeignKey("groups.groupid", ondelete="CASCADE"),
                     primary_key=True)

    userid = Column(String(USER_ID_LENGTH),
                    ForeignKey("users.userid", ondelete="CASCADE"),
                    primary_key=True)

    note = Column(Text, nullable=True)

    group = relationship("Group", back_populates="memberships")
    user = relationship("User", back_populates="memberships")


groups_users = GroupMembership.__table__


def create_additional_groups_users_indexes(table, connection, *args, **kw):
    engine = connection.engine
    if engine.dialect.name != 'sqlite':
        # SQLite 3.7 (as used on Jenkins) doesn't support the syntax yet
        # that SQLAlchemy produces for this functional index
        ix = Index('ix_groups_users_userid_lower',
                   func.lower(groups_users.c.userid))
        ix.create(engine)


event.listen(
    groups_users, 'after_create',
    create_additional_groups_users_indexes)
