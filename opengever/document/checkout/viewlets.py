from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.ogds.base.actor import Actor
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter


class CheckedOutViewlet(ViewletBase):
    """A viewlet which shows a statusmessage like message:
    `This item is being checked out by User XY` when a document
    is checked out."""

    index = ViewPageTemplateFile('templates/checkedoutviewlet.pt')

    def available(self):
        return True

    def update(self):
        manager = queryMultiAdapter((self.context, self.request),
                                    ICheckinCheckoutManager)
        if not manager:
            self.available = False
        elif not manager.get_checked_out_by():
            self.available = False
        else:
            self.available = True

            self.checkout_by_link = Actor.user(
                manager.get_checked_out_by()).get_link()

            self.is_collaborative_checkout = manager.is_collaborative_checkout()
