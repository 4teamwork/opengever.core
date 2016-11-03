from opengever.base.wrapper import SQLWrapperBase
from opengever.locking.interfaces import ISQLLockable
from opengever.meeting.interfaces import IMeetingWrapper
from opengever.meeting.interfaces import IMembershipWrapper
from opengever.meeting.interfaces import IMemberWrapper
from opengever.meeting.interfaces import IPeriodWrapper
from opengever.meeting.model import Membership
from zope.interface import implements


class MeetingWrapper(SQLWrapperBase):

    implements(IMeetingWrapper, ISQLLockable)


class PeriodWrapper(SQLWrapperBase):

    implements(IPeriodWrapper)

    default_view = 'edit'

    def absolute_url(self):
        return self.model.get_url(self.parent)


class MemberWrapper(SQLWrapperBase):

    implements(IMemberWrapper)

    def absolute_url(self):
        return self.model.get_url(self.parent)

    def get_title(self):
        return self.model.fullname

    def __getitem__(self, key):
        if not key.startswith('membership'):
            raise KeyError(key)

        membership_id = int(key.split('-')[-1])
        membership = Membership.query.get(membership_id)
        if not membership:
            raise KeyError(key)

        return MembershipWrapper.wrap(self, membership)


class MembershipWrapper(SQLWrapperBase):

    implements(IMembershipWrapper)

    default_view = 'edit'

    def absolute_url(self):
        return self.model.get_url(self.parent)

    def get_title(self):
        return u'{}, {} - {}'.format(self.model.title(),
                                     self.model.format_date_from(),
                                     self.model.format_date_to())

    def get_breadcrumbs(self):
        my_breadcrumbs = super(MembershipWrapper, self).get_breadcrumbs()
        parent_breadcrumbs = self.parent.get_breadcrumbs()
        return parent_breadcrumbs + my_breadcrumbs
