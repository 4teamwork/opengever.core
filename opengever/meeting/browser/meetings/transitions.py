from opengever.meeting.browser.meetings.meetinglist import MeetingList
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserView


class MeetingTransitionController(BrowserView):

    implements(IBrowserView)

    def __init__(self, context, request, model):
        super(MeetingTransitionController, self).__init__(context, request)
        self.model = model

    def __call__(self):
        transition = self.request.get('transition')
        if not self.is_valid_transition(transition):
            raise NotFound

        self.execute_transition(transition)
        return self.redirect_to_meeting()

    @classmethod
    def url_for(cls, context, meeting, transition):
        return "{}/{}?transition={}".format(
            MeetingList.url_for(context, meeting),
            'meetingtransitioncontroller',
            transition)

    def is_valid_transition(self, transition_name):
        return self.model.can_execute_transition(transition_name)

    def execute_transition(self, transition_name):
        return self.model.execute_transition(transition_name)

    def redirect_to_meeting(self):
        return self.request.RESPONSE.redirect(self.model.get_url())
