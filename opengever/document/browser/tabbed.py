from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.document.interfaces import ICheckinCheckoutManager
from zope.component import getMultiAdapter


class DocumentTabbedView(TabbedView):
    """Tabbedview for documentish types, implements a separate check for the
    uploadbox, to allow drag and drop replacing of a file.
    """

    def show_uploadbox(self):
        """Only checks if a file_upload is available, means document is
        checked out and not locked.
        """

        manager = getMultiAdapter((self.context, self.context.REQUEST),
                                  ICheckinCheckoutManager)

        return manager.is_file_upload_allowed()
