from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.ogds.base.utils import get_current_org_unit
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class InboxTabbedView(TabbedView):

    __call__ = ViewPageTemplateFile("tabbed.pt")

    def current_inbox_title(self):
        return u'{}: {}'.format(self.context.title,
                              get_current_org_unit().label())
