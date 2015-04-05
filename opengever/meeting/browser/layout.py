from opengever.meeting.browser.meetings.meeting import MeetingView
from opengever.meeting.browser.members import MemberView
from plone.app.layout.globals.layout import LayoutPolicy


class CommitteeLayoutPolicy(LayoutPolicy):

    def bodyClass(self, template, view):
        """Extends the default bodyClass if the current view is one of the
        publishTraverse view which just represents an sql object, like a member
        or a meeting we extend the bodyClass with a corresponsing class."""
        body_class = super(CommitteeLayoutPolicy, self).bodyClass(
            template, view)

        if isinstance(view, MemberView):
            body_class = ' '.join((body_class, 'member-view'))

        if isinstance(view, MeetingView):
            body_class = ' '.join((body_class, 'meeting-view'))

        return body_class
