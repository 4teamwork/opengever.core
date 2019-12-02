from opengever.base.wrapper import SQLWrapperBase
from opengever.locking.interfaces import ISQLLockable
from opengever.meeting.interfaces import IMeetingWrapper
from opengever.meeting.interfaces import IMembershipWrapper
from opengever.meeting.interfaces import IMemberWrapper
from zope.interface import implements


class MeetingWrapper(SQLWrapperBase):
    """SQLWrapper for meeting objects.
    """

    implements(IMeetingWrapper, ISQLLockable)


class MemberWrapper(SQLWrapperBase):
    """SQLWrapper for member objects.
    """

    implements(IMemberWrapper)

    def absolute_url(self):
        return self.model.get_url(self.parent)

    def get_title(self):
        return self.model.fullname


class MembershipWrapper(SQLWrapperBase):
    """SQLWrapper for membership objects.
    """

    implements(IMembershipWrapper)

    default_view = 'edit'

    def absolute_url(self):
        committee = self.model.committee.resolve_committee()
        return self.model.get_url(committee)

    def get_title(self):
        return u'{}, {} - {}'.format(self.model.title(),
                                     self.model.format_date_from(),
                                     self.model.format_date_to())
