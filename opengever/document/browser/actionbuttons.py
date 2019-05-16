from opengever.document import _
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.officeconnector.helpers import is_officeconnector_attach_feature_enabled  # noqa
from opengever.onlyoffice import is_onlyoffice_feature_enabled
from opengever.onlyoffice.config import SUPPORTED_TYPES
from opengever.webactions.interfaces import IWebActionsRenderer
from opengever.wopi.interfaces import IWOPISettings
from opengever.wopi import is_wopi_feature_enabled
from plone import api
from plone.locking.interfaces import IRefreshableLockable
from plone.protect import createToken
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.i18n import translate
import os.path


class ActionButtonRendererMixin(object):
    """Mixin for views that render action buttons."""

    is_overview_tab = False
    is_on_detail_view = False
    overlay = None

    def is_edit_metadata_link_visible(self):
        if self.is_overview_tab:
            return False

        if self.is_versioned():
            return False

        return True

    def is_locked(self):
        return IRefreshableLockable(self.context).locked()

    def is_edit_metadata_available(self):
        # XXX object orient me, the object should know some of this stuff
        if self.is_checked_out_by_another_user():
            return False

        if self.is_locked():
            return False

        return api.user.has_permission(
            'Modify portal content',
            obj=self.context,
            )

    def is_versioned(self):
        return self.request.get('version_id') is not None

    def is_office_connector_editable(self):
        return self.context.is_office_connector_editable()

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

        return not self.is_checked_out_by_another_user()

    def get_download_copy_tag(self):
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

    def is_document(self):
        return IDocumentSchema.providedBy(self.context)

    def is_oneoffixx_creatable(self):
        return self.is_document() and self.context.is_oneoffixx_creatable()

    def is_wopi_editable(self):
        if not self.is_document() or not is_wopi_feature_enabled():
            return False
        if not self.context.file:
            return False
        basename, extension = os.path.splitext(self.context.file.filename)
        if extension in ['.docx', '.xlsx', '.pptx']:
            return True
        return False

    def is_onlyoffice_editable(self):
        if not self.is_document() or not is_onlyoffice_feature_enabled():
            return False
        if not self.context.file:
            return False
        basename, extension = os.path.splitext(self.context.file.filename)
        if extension in SUPPORTED_TYPES:
            return True
        return False

    def is_attach_to_email_available(self):
        if not is_officeconnector_attach_feature_enabled():
            return False

        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)
        if manager is None:
            # This is probably a mail
            return True

        return not self.is_checked_out_by_another_user()

    def is_checked_out(self):
        return self.context.is_checked_out()

    def is_checked_out_by_another_user(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        if not manager:
            return False

        checked_out_by = manager.get_checked_out_by()
        if not checked_out_by:
            return False

        return checked_out_by != api.user.get_current().getId()

    def is_checked_out_by_current_user(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)
        if manager is None:
            # This is probably a mail
            return False

        return manager.is_checked_out_by_current_user()

    def is_detail_view_link_available(self):
        return not self.is_on_detail_view

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

        if not manager:
            # This is probably a mail
            return False

        return manager.is_checkin_allowed()

    def is_checkout_cancel_available(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        if not manager:
            return False

        return manager.is_cancel_allowed()

    def get_checkout_cancel_tag(self):
        if not self.has_file() or not self.is_checkout_cancel_available():
            return None
        clazz = 'link-overlay modal function-revert'
        url = u'{}/@@cancel_document_checkout_confirmation'.format(
            self.context.absolute_url())
        label = translate(_(u'Cancel checkout'),
                          context=self.request).encode('utf-8')
        return ('<a href="{0}" '
                'id="action-cancel-checkout" '
                'class="{1}">{2}</a>').format(url, clazz, label)

    def has_file(self):
        return self.context.has_file()

    def get_file(self):
        return self.context.get_file()

    def get_url(self):
        return self.context.absolute_url()

    def get_webaction_items(self):
        renderer = getMultiAdapter((self.context, self.request),
                                   IWebActionsRenderer, name='action-buttons')
        return renderer()
