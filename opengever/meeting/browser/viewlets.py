from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.ogds.base.actor import Actor
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter


class ProposalInfoViewlet(ViewletBase):
    """Show a statusmessages that a proposals document is checked out."""

    index = ViewPageTemplateFile('templates/proposalinfoviewlet.pt')

    def show_checkout_info(self):
        return self.context.contains_checked_out_documents()

    def checkout_by_link(self):
        document = self.context.get_proposal_document()

        manager = queryMultiAdapter((document, self.request),
                                    ICheckinCheckoutManager)
        return Actor.user(manager.get_checked_out_by()).get_link()
