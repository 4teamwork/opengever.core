from datetime import datetime
from datetime import time
from opengever.base.model import Base
from opengever.meeting.model.query import MembershipQuery
from plone import api
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Membership(Base):
    """Associate members with their commmission for a certain timespan.

    """
    query_cls = MembershipQuery

    __tablename__ = 'memberships'
    __table_args__ = (UniqueConstraint('committee_id',
                                       'member_id',
                                       'date_from',
                                       name='ix_membership_unique'), {})

    membership_id = Column("id", Integer, Sequence("membership_id_seq"),
                           primary_key=True)

    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)

    committee_id = Column(Integer, ForeignKey('committees.id'))
    committee = relationship("Committee", backref="memberships")
    member_id = Column(Integer, ForeignKey('members.id'))
    member = relationship("Member", backref="memberships")
    role = Column(String(256))

    def __repr__(self):
        return '<Membership {} in {} {}:{}>'.format(
            repr(self.member.fullname),
            repr(self.committee.title),
            self.date_from,
            self.date_to)

    def is_editable(self):
        return True

    def format_date_from(self):
        return self._format_date(self.date_from)

    def format_date_to(self):
        if not self.date_to:
            return ''

        return self._format_date(self.date_to)

    def _format_date(self, date):
        return api.portal.get_localized_time(
            datetime=datetime.combine(date, time()))

    def title(self):
        return self.member.fullname

    def get_edit_values(self, fieldnames):
        values = {}
        for fieldname in fieldnames:
            value = getattr(self, fieldname, None)
            if value:
                values[fieldname] = value

        return values

    def update_model(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def get_url(self, context):
        return "{}/membership/{}".format(context.absolute_url(),
                                         self.membership_id)

    def get_edit_url(self, context):
        return '/'.join((self.get_url(context), 'edit'))

    def get_remove_url(self, context):
        return '/'.join((self.get_url(context), 'remove'))

    def get_breadcrumbs(self, context):
        return {'absolute_url': self.get_url(context), 'Title': self.title}
