from opengever.document.document import _
from opengever.document.interfaces import ICheckinCheckoutManager
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter


class RevertFileToVersion(BrowserView):
    """Reverts the file of a document to a specific version.
    """
    def __call__(self):
        version_id = self.request.get('version_id')

        # revert the file
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)
        manager.revert_to_version(version_id)

        # create a status message
        msg = _(u'Reverted file to version ${version_id}.',
                mapping=dict(version_id=version_id))
        IStatusMessage(self.request).addStatusMessage(msg, type='info')

        # redirect back to file view
        return self.request.RESPONSE.redirect(self.context.absolute_url())
