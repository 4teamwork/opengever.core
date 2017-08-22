from datetime import datetime
from datetime import time
from opengever.base.model import Base
from opengever.base.model import SQLFormSupport
from plone import api
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Membership(Base, SQLFormSupport):
    """Associate members with their commmission for a certain timespan.

    """
    __tablename__ = 'memberships'
    __mapper_args__ = {'order_by': 'date_from'}
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

    @property
    def css_class(self):
        return 'contenttype-opengever-meeting-membership'

    def is_removable(self):
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

    def get_url(self, context, view=None):
        parts = [
            context.absolute_url(),
            'membership-{}'.format(self.membership_id),
        ]
        if view:
            parts.append(view)
        return '/'.join(parts)

    def get_remove_url(self):
        committee = self.committee.resolve_committee()
        if committee:
            return self.get_url(committee, view='remove')

    def get_edit_url(self):
        committee = self.committee.resolve_committee()
        if committee:
            return self.get_url(committee, view='edit')
