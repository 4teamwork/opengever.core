from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.task import _
from opengever.task.browser.accept.utils import \
    accept_forwarding_with_successor
from zope.component import getUtility


class CreateSuccesorForwardingView(grok.View):
    """View wich create a succesor forwarding in the current inbox,
    and store the remote forwarding in the yearfolder.
    """

    grok.context(IPloneSiteRoot)
    grok.name('accept_store_in_inbox')
    grok.require('zope2.View')

    def render(self):
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
