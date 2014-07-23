from ftw.tabbedview.browser.tabbed import TabbedView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class InboxTabbedView(TabbedView):

    def __call__(self):
        current_inbox = self.context.get_current_inbox()

        if self.context.is_main_inbox():
            if self.context != current_inbox:
                return self.request.RESPONSE.redirect(
                    current_inbox.absolute_url())

        return ViewPageTemplateFile("tabbed.pt")(self)
