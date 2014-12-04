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
        return self.redirect_to_proposal()

    def is_valid_transition(self, transition_name):
        return self.context.can_perform_transition(transition_name)

    def execute_transition(self, transition_name):
        return self.context.perform_transition(transition_name)

    def redirect_to_proposal(self):
        return self.request.RESPONSE.redirect(self.context.absolute_url())
