from opengever.core.model import Base
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship


class Membership(Base):
    """Associate members with their commmission for a certain timespan.

    """
    __tablename__ = 'memberships'

    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)

    commission_id = Column(Integer, ForeignKey('commissions.id'),
                           primary_key=True)
    commission = relationship("Commission", backref="memberships")
    member_id = Column(Integer, ForeignKey('members.id'),
                       primary_key=True)
    member = relationship("Member", backref="memberships")

    def __repr__(self):
        return '<Membership "{}" in "{}" {}:{}>'.format(
            self.member.fullname,
            self.commission.title,
            self.date_from,
            self.date_to)
