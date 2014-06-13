from five import grok
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.ogds.base.actor import Actor
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.interfaces import IAboveContent
from zope.component import queryMultiAdapter


class CheckedOutViewlet(grok.Viewlet):
    """A viewlet which shows a statusmessage like message:
    `This item is being checked out by User XY` when a document
    is checked out."""

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

            self.checkout_by_link = Actor.user(manager.checked_out()).get_link()
