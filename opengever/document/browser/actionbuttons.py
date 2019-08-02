from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.document.interfaces import IFileActions
from opengever.officeconnector.helpers import is_officeconnector_attach_feature_enabled  # noqa
from opengever.webactions.interfaces import IWebActionsRenderer
from plone import api
from plone.protect import createToken
from Products.Five.browser import BrowserView
from urllib import quote
from zope.component import getMultiAdapter
import os


class FileActionAvailabilityMixin(object):
    """Mixin that delegates availability checks to an IFileActions adapter.

    Returns whether an action is available. An action which is not available
    cannot be performed by the model in its current state.
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

    def is_open_as_pdf_action_available(self):
        return self.ifileactions.is_open_as_pdf_action_available()

    def is_revert_to_version_action_available(self):
        return self.ifileactions.is_revert_to_version_action_available()


class FileActionAvailabilityView(BrowserView, FileActionAvailabilityMixin):
    """View that exposes file action availaibility."""


class VisibleActionButtonRendererMixin(FileActionAvailabilityMixin):
    """Mixin to render the `file_action_buttons` macro.

    Adds the notion of visibility to certain actions. Also decides about
    visibility of other non -action elements in the macro.
    If an action is visible it must always be available. The view can decide
    to make an available action invisible however.

    """
    overlay = None

    def is_oc_unsupported_file_discreet_edit_visible(self):
        return (self.ifileactions.is_any_checkout_or_edit_available()
                and not self.context.is_office_connector_editable()
                and self.context.is_checked_out())

    def is_discreet_no_file_hint_visible(self):
        return not self.context.has_file()

    def is_edit_metadata_action_visible(self):
        return self.is_edit_metadata_action_available()

    def is_discreet_edit_metadata_action_visible(self):
        return not self.is_edit_metadata_action_visible()

    def is_detail_view_link_visible(self):
        return False

    def is_attach_to_email_action_set_visible(self):
        """Only show the actions if the feature is enabled."""

        return is_officeconnector_attach_feature_enabled()

    def is_open_as_pdf_action_visible(self):
        return False

    def get_oc_direct_checkout_url(self):
        return (
            u"javascript:officeConnectorCheckout("
            "'{}/officeconnector_checkout_url'"
            ");".format(self.context.absolute_url()))

    def get_oc_attach_to_email_url(self):
        return (
            u"javascript:officeConnectorAttach("
            "'{}/officeconnector_attach_url'"
            ");".format(self.context.absolute_url()))

    def get_oc_oneoffixx_retry_url(self):
        return (
            u"javascript:officeConnectorCheckout("
            "'{}/officeconnector_oneoffixx_url'"
            ");".format(self.context.absolute_url()))

    def get_oc_zem_checkout_url(self):
        return u'{}/editing_document?_authenticator={}'.format(
            self.context.absolute_url(),
            createToken())

    def get_checkout_url(self):
        return "{}/@@checkout_documents?_authenticator={}".format(
            self.context.absolute_url(),
            createToken())

    def get_open_as_pdf_url(self):
        if not self.is_open_as_pdf_action_available():
            return None

        return u'{}/bumblebee-open-pdf?filename={}'.format(
            self.context.absolute_url(),
            quote(self._get_pdf_filename().encode('utf-8')))

    def _get_pdf_filename(self):
        filename = os.path.splitext(self.context.get_file().filename)[0]
        return u'{}.pdf'.format(filename)

    def should_pdfs_open_in_new_window(self):
        return api.portal.get_registry_record(
            'open_pdf_in_a_new_window',
            interface=IGeverBumblebeeSettings)

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
