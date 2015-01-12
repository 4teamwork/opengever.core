from opengever.core.model import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import column_property
from sqlalchemy.schema import Sequence


class Member(Base):

    __tablename__ = 'members'

    member_id = Column("id", Integer, Sequence("member_id_seq"),
                       primary_key=True)
    firstname = Column(String(256), nullable=False)
    lastname = Column(String(256), nullable=False)
    fullname = column_property(firstname + " " + lastname)
    email = Column(String(256))

    def __repr__(self):
        return '<Member {}>'.format(repr(self.fullname))
