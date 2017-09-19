from opengever.base.response import JSONResponse
from opengever.meeting import _
from plone.protect.utils import addTokenToUrl
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserView


class MeetingTransitionController(BrowserView):

    implements(IBrowserView)

    def __init__(self, context, request):
        super(MeetingTransitionController, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        transition = self.request.get('transition')
        if not self.is_valid_transition(transition):
            raise NotFound

        self.execute_transition(transition)
        msg = _('label_transition_executed',
                default='Transition ${transition} executed',
                mapping={'transition': self.model.workflow.transitions.get(transition).title})

        return JSONResponse(self.request).redirect(self.model.get_url()).info(msg).dump();

    @classmethod
    def url_for(cls, context, meeting, transition):
        url = '{}?transition={}'.format(
            meeting.get_url(view='meetingtransitioncontroller'), transition)
        return addTokenToUrl(url)

    def is_valid_transition(self, transition_name):
        return self.model.can_execute_transition(transition_name)

    def execute_transition(self, transition_name):
        return self.model.execute_transition(transition_name)
