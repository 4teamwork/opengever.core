from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.task import _
from opengever.task.browser.accept.utils import accept_forwarding_with_successor
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility
from zope.interface import alsoProvides


class CreateSuccesorForwardingView(BrowserView):
    """View wich create a succesor forwarding in the current inbox,
    and store the remote forwarding in the yearfolder.
    """

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        oguid = self.request.get('oguid')
        key = 'accept:%s' % oguid
        dm = getUtility(IWizardDataStorage)
        text = dm.get(key, 'text')

        # forwarding
        if dm.get(key, 'is_forwarding'):
            forwarding = accept_forwarding_with_successor(
                self.context, oguid, text)
            IStatusMessage(self.request).addStatusMessage(
                _(u'The forwarding has been stored in the local inbox'),
                'info')
            self.request.RESPONSE.redirect(forwarding.absolute_url())
