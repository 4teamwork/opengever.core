from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.document.interfaces import IFileActions
from opengever.webactions.interfaces import IWebActionsRenderer
from plone.protect import createToken
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter


class FileActionAvailabilityChecker(object):
    """Mixin containing the methods to check whether certain
    actions should be available on a document.
    """
    @property
    def ifileactions(self):
        return getMultiAdapter((self.context, self.request), IFileActions)

    def is_edit_metadata_action_available(self):
        return self.ifileactions.is_edit_metadata_action_available()

    def has_file(self):
        """Check whether the context has a file"""
        return self.context.has_file()

    def is_versioned(self):
        return self.request.get('version_id') is not None

    def is_checked_out(self):
        return self.context.is_checked_out()

    def is_any_checkout_or_edit_available(self):
        return self.ifileactions.is_any_checkout_or_edit_available()

    def is_oc_direct_edit_action_available(self):
        return self.ifileactions.is_oc_direct_edit_action_available()

    def is_oc_direct_checkout_action_available(self):
        return self.ifileactions.is_oc_direct_checkout_action_available()

    def is_oc_zem_checkout_action_available(self):
        return self.ifileactions.is_oc_zem_checkout_action_available()

    def is_oc_zem_edit_action_available(self):
        return self.ifileactions.is_oc_zem_edit_action_available()

    def is_oc_unsupported_file_checkout_action_available(self):
        return self.ifileactions.is_oc_unsupported_file_checkout_action_available()

    def is_checkin_without_comment_available(self):
        return self.ifileactions.is_checkin_without_comment_available()

    def is_checkin_with_comment_available(self):
        return self.ifileactions.is_checkin_with_comment_available()

    def is_cancel_checkout_action_available(self):
        return self.ifileactions.is_cancel_checkout_action_available()

    def is_download_copy_action_available(self):
        return self.ifileactions.is_download_copy_action_available()

    def is_attach_to_email_action_available(self):
        return self.ifileactions.is_attach_to_email_action_available()

    def is_oneoffixx_retry_action_available(self):
        return self.ifileactions.is_oneoffixx_retry_action_available()


class FileActionAvailabilityCheckerView(BrowserView, FileActionAvailabilityChecker):
    """View used to check the availability of file actions
    """


class ActionButtonRendererMixin(FileActionAvailabilityChecker):
    """Mixin for views that render action buttons."""

    is_overview_tab = False
    is_on_detail_view = False
    overlay = None

    def is_oc_unsupported_file_edit_action_available(self):
        return (self.ifileactions.is_any_checkout_or_edit_available()
                and not self.context.is_office_connector_editable()
                and self.context.is_checked_out())

    def is_edit_metadata_link_visible(self):
        if self.is_overview_tab:
            return False

        if self.is_versioned():
            return False

        return True

    def is_detail_view_link_available(self):
        return not self.is_on_detail_view

    def render_download_copy_link(self):
        """Returns the DownloadConfirmationHelper tag containing
        the donwload link. For mails, containing an original_message, the tag
        links to the orginal message download view.
        """
        dc_helper = DownloadConfirmationHelper(self.context)

        kwargs = {
            'additional_classes': ['function-download-copy'],
            'viewname': self.context.get_download_view_name(),
            'include_token': True,
            }

        requested_version_id = self.request.get('version_id')

        if requested_version_id:
            requested_version_id = int(requested_version_id)
            current_version_id = self.context.get_current_version_id()

            if requested_version_id != current_version_id:
                kwargs['url_extension'] = (
                    '?version_id={}'
                    .format(requested_version_id)
                    )

        return dc_helper.get_html_tag(**kwargs)

    def get_checkin_without_comment_url(self):
        if not self.is_checkin_without_comment_available():
            return None
        return self._get_checkin_url(with_comment=False)

    def get_checkin_with_comment_url(self):
        if not self.is_checkin_with_comment_available():
            return None
        return self._get_checkin_url(with_comment=True)

    def _get_checkin_url(self, with_comment=False):
        if with_comment:
            checkin_view = u'@@checkin_document'
        else:
            checkin_view = u'@@checkin_without_comment'

        return u"{}/{}?_authenticator={}".format(
            self.context.absolute_url(),
            checkin_view,
            createToken())

    def get_cancel_checkout_url(self):
        return u'{}/@@cancel_document_checkout_confirmation'.format(
            self.context.absolute_url())

    def get_file(self):
        return self.context.get_file()

    def get_webaction_items(self):
        renderer = getMultiAdapter((self.context, self.request),
                                   IWebActionsRenderer, name='action-buttons')
        return renderer()
