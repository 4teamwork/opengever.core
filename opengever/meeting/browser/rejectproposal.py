from opengever.base.request import safe_call
from plone import api
from Products.Five import BrowserView


@safe_call
class RejectProposal(BrowserView):

    def __call__(self):
        api.content.transition(obj=self.context,
                               transition='proposal-transition-reject')
        return 'OK'
