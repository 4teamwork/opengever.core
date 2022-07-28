from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.ogds.base.actor import Actor
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter


class DocumentStatusMessageViewlet(ViewletBase):
    """A viewlet which shows a statusmessage like message:
    `This item is being checked out by User XY` when a document
    is checked out."""

    index = ViewPageTemplateFile('templates/document_status_message_viewlet.pt')

    def __init__(self, context, request, view, manager=None):
        super(DocumentStatusMessageViewlet, self).__init__(context, request, view, manager=manager)
        self.checked_out = False
        self.is_final = False

    def available(self):
        return self.checked_out or self.is_final

    def update(self):
        self.update_checked_out()
        self.update_finalized()

    def update_checked_out(self):
        manager = queryMultiAdapter((self.context, self.request),
                                    ICheckinCheckoutManager)
        if not manager:
            self.checked_out = False
        elif not manager.get_checked_out_by():
            self.checked_out = False
        else:
            self.checked_out = True

            self.checkout_by_link = Actor.user(
                manager.get_checked_out_by()).get_link()

            self.is_collaborative_checkout = manager.is_collaborative_checkout()

    def update_finalized(self):
        if self.context.is_final_document():
            self.is_final = True
