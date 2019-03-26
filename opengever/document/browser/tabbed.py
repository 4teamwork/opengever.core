from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.document import _
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.trash.trash import ITrashed
from plone import api
from zope.component import getMultiAdapter


class DocumentTabbedView(TabbedView):
    """Tabbedview for documentish types, implements a separate check for the
    uploadbox, to allow drag and drop replacing of a file.
    """

    def __init__(self, context, request):
        """Slap a warning onto the overview of a trashed document.

        We're asserting on the request not having a form as the tabs themselves,
        which get requested by AJAX, rely on a form in the request data. If
        we'd also slap the portal warning onto those requests, the next 'full'
        page view would display them, as the tabs do not consume a portal
        warning.
        """
        super(DocumentTabbedView, self).__init__(context, request)
        if ITrashed.providedBy(self.context):
            if not self.request.form:
                msg = _(
                    u'warning_trashed', default=u'This document is trashed.')
                api.portal.show_message(msg, self.request, type='warning')

    def show_uploadbox(self):
        """Only checks if a file_upload is available, means document is
        checked out and not locked.
        """

        manager = getMultiAdapter((self.context, self.context.REQUEST),
                                  ICheckinCheckoutManager)

        return manager.is_file_upload_allowed()
