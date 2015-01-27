from five import grok
from opengever.meeting.browser import meetings
from opengever.meeting.committee import ICommittee
from opengever.meeting.model import Meeting
from zExceptions import NotFound
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class MeetingList(grok.View):

    implements(IPublishTraverse)
    grok.context(ICommittee)
    grok.name('meeting')

    @classmethod
    def url_for(cls, context, meeting):
        return "{}/{}/{}".format(
            context.absolute_url(), cls.__view_name__, meeting.meeting_id)

    def render(self):
        """This view is never rendered directly.

        This method ist still needed to make grok checks happy, every grokked
        view must have an associated template or 'render' method.

        """
        pass

    def publishTraverse(self, request, name):
        """Allows us to handle URLs like ../committee-3/meeting/42.

        Note that meetings are stored in a relational database only and not as
        plone content.

        """
        try:
            meeting_id = int(name)
        except ValueError:
            raise NotFound

        meeting = Meeting.query.get(meeting_id)
        if meeting is None:
            raise NotFound

        return meetings.meeting.MeetingView(self.context, self.request, meeting)
