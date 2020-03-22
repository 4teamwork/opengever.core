from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.document.interfaces import IFileActions
from opengever.officeconnector.helpers import is_officeconnector_attach_feature_enabled  # noqa
from opengever.webactions.interfaces import IWebActionsRenderer
from plone import api
from plone.protect.utils import addTokenToUrl
from Products.Five.browser import BrowserView
from urllib import quote
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
import os


class FileActionAvailabilityMixin(object):
    """Mixin that delegates availability checks to an IFileActions adapter.

    Returns whether an action is available. An action which is not available
    cannot be performed by the model in its current state.
    """
    @property
    def ifileactions(self):
        return queryMultiAdapter((self.context, self.request), IFileActions)

    def __getattr__(self, name):
        """We overwrite this method which will only be called if the given
        attribute is not present on the derived class. In that case we get
        it from the IFileActions adapter if there is one registered for the
        context.
        """
        if name not in IFileActions:
            raise AttributeError
        # We return a lambda here, as IFileActions only defines methods
        return getattr(self.ifileactions, name, lambda: False)


class FileActionAvailabilityView(BrowserView, FileActionAvailabilityMixin):
    """View that exposes file action availaibility."""


class VisibleActionButtonRendererMixin(FileActionAvailabilityMixin):
    """Mixin to render the `file_action_buttons` macro.

    Adds the notion of visibility to certain actions. Also decides about
    visibility of other non -action elements in the macro.
    If an action is visible it must always be available. The view can decide
    to make an available action invisible however.

    """
    def get_edit_metadata_url(self):
        return u'{}/edit_checker'.format(self.context.absolute_url())

    def is_oc_unsupported_file_discreet_edit_visible(self):
        return (self.is_any_checkout_or_edit_available()
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
        url = u'{}/editing_document'.format(self.context.absolute_url())
        return addTokenToUrl(url)

    def get_checkout_url(self):
        url = "{}/@@checkout_documents".format(self.context.absolute_url())
        return addTokenToUrl(url)

    def get_office_online_edit_url(self):
        return u'{}/office_online_edit'.format(self.context.absolute_url())

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

        url = u"{}/{}".format(self.context.absolute_url(), checkin_view)
        return addTokenToUrl(url)

    def get_cancel_checkout_url(self):
        return u'{}/@@cancel_document_checkout_confirmation'.format(
            self.context.absolute_url())

    def get_revert_to_version_url(self):
        url = u'{}/revert-file-to-version?version_id={}'.format(
            self.context.absolute_url(),
            self.request.get('version_id'))
        return addTokenToUrl(url)

    def get_webaction_items(self):
        renderer = getMultiAdapter((self.context, self.request),
                                   IWebActionsRenderer, name='action-buttons')
        return renderer()
