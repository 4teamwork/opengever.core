from opengever.base.pdfconverter import is_pdfconverter_enabled
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.document.interfaces import ICheckinCheckoutManager
from plone import api
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.locking.interfaces import IRefreshableLockable
from plone.protect import createToken
from zope.component import queryMultiAdapter


class ActionButtonRendererMixin(object):
    """Mixin for views that render action buttons."""

    is_overview_tab = False
    on_detail_view = False
    overlay = None

    def is_edit_metadata_available(self):
        if self.is_overview_tab:
            return False

        if self.is_versioned():
            return False

        if self.context.is_checked_out():
            return False

        if IRefreshableLockable(self.context).locked():
            return False

        return not IContentListingObject(self.context).is_trashed

    def is_versioned(self):
        return self.request.get('version_id') is not None

    def is_preview_supported(self):
        # XXX TODO: should be persistent called two times
        if is_pdfconverter_enabled():
            return True
        return False

    def is_checkout_and_edit_available(self):
        if self.is_versioned():
            return False
        return self.context.is_checkout_and_edit_available()

    def is_download_copy_available(self):
        """Disable downloading copies when the document is checked out by an
        another user.
        """
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)
        if manager is None:
            # This is probably a mail
            return True

        checkout = manager.get_checked_out_by()
        if checkout and checkout != api.user.get_current().getId():
            return False

        return True

    def get_download_copy_tag(self):
        dc_helper = DownloadConfirmationHelper()
        return dc_helper.get_html_tag(
            self.context.absolute_url(),
            additional_classes=['function-download-copy'],
            include_token=True,
            )

    def is_checked_out_by_current_user(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)
        if manager is None:
            # This is probably a mail
            return False

        return manager.is_checked_out_by_current_user()

    def get_checkin_without_comment_url(self):
        if not self.has_file():
            return None
        return self._get_checkin_url(with_comment=False)

    def get_checkin_with_comment_url(self):
        if not self.has_file():
            return None
        return self._get_checkin_url(with_comment=True)

    def _get_checkin_url(self, with_comment=False):
        if not self._is_checkin_allowed():
            return None

        if with_comment:
            checkin_view = u'@@checkin_document'
        else:
            checkin_view = u'@@checkin_without_comment'

        return u"{}/{}?_authenticator={}".format(
            self.context.absolute_url(),
            checkin_view,
            createToken())

    def _is_checkin_allowed(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        return manager.is_checkin_allowed()

    def has_file(self):
        return self.context.has_file()

    def get_file(self):
        return self.context.get_file()

    def get_url(self):
        return self.context.absolute_url()
