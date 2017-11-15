from opengever.base.request import tracebackify
from Products.Five import BrowserView


@tracebackify
class RejectProposal(BrowserView):

    def __call__(self):
        self.context.reject()
        return 'OK'
