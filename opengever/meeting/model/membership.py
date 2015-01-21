from opengever.base.model import Base
from opengever.meeting.model.query import MembershipQuery
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship


class Membership(Base):
    """Associate members with their commmission for a certain timespan.

    """
    query_cls = MembershipQuery

    __tablename__ = 'memberships'

    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)

    committee_id = Column(Integer, ForeignKey('committees.id'),
                           primary_key=True)
    committee = relationship("Committee", backref="memberships")
    member_id = Column(Integer, ForeignKey('members.id'),
                       primary_key=True)
    member = relationship("Member", backref="memberships")

    def __repr__(self):
        return '<Membership {} in {} {}:{}>'.format(
            repr(self.member.fullname),
            repr(self.committee.title),
            self.date_from,
            self.date_to)
