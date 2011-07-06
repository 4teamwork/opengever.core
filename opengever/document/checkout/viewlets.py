from five import grok
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.ogds.base.interfaces import IContactInformation
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.interfaces import IAboveContent
from zope.component import getUtility
from zope.component import queryMultiAdapter


class CheckedOutViewlet(grok.Viewlet):

    grok.viewletmanager(IAboveContent)
    grok.context(IDocumentSchema)
    grok.view(IViewView)
    grok.require('zope2.View')

    def update(self):
        manager = queryMultiAdapter((self.context, self.request),
                                    ICheckinCheckoutManager)
        if not manager:
            self.available = False
        elif not manager.checked_out():
            self.available = False
        else:
            self.available = True

            info = getUtility(IContactInformation)
            owner_id = manager.checked_out()
            self.checkout_owner = info.render_link(owner_id)
