from five import grok
from opengever.meeting.proposal import IProposal
from zExceptions import NotFound


class ProposalTransitionController(grok.View):
    grok.context(IProposal)
    grok.name('proposaltransitioncontroller')
    grok.require('zope2.View')

    @classmethod
    def url_for(cls, context, transition):
        return "{}/@@{}?transition={}".format(
            context.absolute_url(), cls.__view_name__, transition)

    def render(self):
        transition = self.request.get('transition')
        if not self.is_valid_transition(transition):
            raise NotFound

        self.execute_transition(transition)

    def is_valid_transition(self, transition_name):
        pass

    def execute_transition(self, transition_name):
        pass
