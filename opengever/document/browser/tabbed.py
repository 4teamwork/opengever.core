from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.document.interfaces import ICheckinCheckoutManager
from zope.component import getMultiAdapter


class DocumentTabbedView(TabbedView):

    def show_uploadbox(self):
        manager = getMultiAdapter((self.context, self.context.REQUEST),
                                  ICheckinCheckoutManager)

        if not manager.is_file_upload_allowed():
            return False

        return super(DocumentTabbedView, self).show_uploadbox()
