from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import Redirect
import transaction


class ForbiddenByQuotaView(BrowserView):

    def __call__(self):
        # this is an error, we must not commit
        transaction.abort()
        IStatusMessage(self.request).addStatusMessage(
            self.context.message, type='error')
        raise Redirect(self.context.container.absolute_url() + '/usage')
