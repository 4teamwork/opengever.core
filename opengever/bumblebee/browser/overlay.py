from Acquisition import aq_parent
from ftw import bumblebee
from ftw.bumblebee.mimetypes import is_mimetype_supported
from ftw.bumblebee.interfaces import IBumblebeeDocument
from opengever.base.browser.helper import get_css_class
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.base.protect import unprotected_write
from opengever.bumblebee import _
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee.interfaces import IBumblebeeOverlay
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.bumblebee.interfaces import IVersionedContextMarker
from opengever.document.browser.actionbuttons import ActionButtonRendererMixin
from opengever.document.browser.versions_tab import translate_link
from opengever.document.checkout.viewlets import CheckedOutViewlet
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.locking.info import GeverLockInfoViewlet
from opengever.mail.mail import IOGMailMarker
from opengever.ogds.base.actor import Actor
from plone import api
from plone.protect import createToken
from plone.protect.utils import addTokenToUrl
from Products.CMFEditions.interfaces.IArchivist import ArchivistRetrieveError
from Products.Five import BrowserView
from urllib import quote
from zExceptions import NotFound
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
import os


@implementer(IBumblebeeOverlay)
@adapter(IDocumentSchema, Interface)
class BumblebeeBaseDocumentOverlay(ActionButtonRendererMixin):
    """Bumblebee overlay for base documents.
    """

    version_id = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_latest_version(self):
        """A documentish without versions is always the latest version."""
        return True

    def get_preview_pdf_url(self):
        return bumblebee.get_service_v3().get_representation_url(
            self.context, 'preview')

    def get_bumblebee_checksum(self):
        return IBumblebeeDocument(self.context).get_checksum()

    def get_mime_type_css_class(self):
        return get_css_class(self.context)

    def get_creator_link(self):
        return Actor.user(self.context.Creator()).get_link()

    def get_document_date(self):
        return api.portal.get_localized_time(self.context.document_date)

    def get_containing_dossier(self):
        return self.context.get_parent_dossier()

    def get_sequence_number(self):
        return getUtility(ISequenceNumber).get_number(self.context)

    def get_reference_number(self):
        return getAdapter(self.context, IReferenceNumber).get_number()

    def get_edit_metadata_url(self):
        if not api.user.has_permission(
                'Modify portal content', obj=self.context):
            return None

        return u'{}/edit'.format(self.context.absolute_url())

    def get_detail_view_url(self):
        return self.context.absolute_url()

    def get_title(self):
        return self.context.title

    def get_description(self):
        return self.context.description

    def get_file_size(self):
        """Return the filesize in KB."""
        return self.get_file().getSize() / 1024 if self.has_file() else None

    def get_filename(self):
        return self.get_file().filename if self.has_file() else None

    def get_checkout_url(self):
        if not self.has_file() or not self._is_checkout_and_edit_available():
            return None

        return u'{}/editing_document?_authenticator={}'.format(
            self.context.absolute_url(),
            createToken())

    def get_download_copy_link(self):
        # Because of cyclic dependencies, we can not import
        # DownloadConfirmationHelper in the top of the file.
        from opengever.document.browser.download import DownloadConfirmationHelper  # noqa

        if not self.has_file():
            return None

        dc_helper = DownloadConfirmationHelper(self.context)
        return dc_helper.get_html_tag(
            additional_classes=['function-download-copy'],
            include_token=True
            )

    def get_open_as_pdf_url(self):
        mimetypeitem = self.context.get_mimetype()
        if not mimetypeitem or not is_mimetype_supported(mimetypeitem[0]):
            return None

        return u'{}/bumblebee-open-pdf?filename={}'.format(
            self.context.absolute_url(), quote(self._get_pdf_filename()))

    def render_checked_out_viewlet(self):
        viewlet = CheckedOutViewlet(self.context, self.request, None, None)
        viewlet.update()
        return viewlet.render()

    def render_lock_info_viewlet(self):
        viewlet = GeverLockInfoViewlet(self.context, self.request, None, None)
        viewlet.update()
        return viewlet.render()

    def get_revert_link(self):
        if self.is_versioned():
            return self._get_revert_link()
        return None

    def _get_pdf_filename(self):
        if not self.has_file():
            # Bumblebee will use a placeholder filename
            return None

        filename = os.path.splitext(self.get_file().filename)[0]
        return u'{}.pdf'.format(filename)

    def _is_checkout_and_edit_available(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        userid = manager.get_checked_out_by()

        if not userid:
            return manager.is_checkout_allowed()
        return userid == api.user.get_current().getId()

    def _get_revert_link(self):
        url = u'{}/revert-file-to-version?version_id={}'.format(
            self.context.absolute_url(),
            self.version_id)

        url = addTokenToUrl(url)

        return translate_link(
            url, _(u'label_revert', default=u'Revert document'),
            css_class='standalone function-revert')

    def should_open_in_new_window(self):
        return api.portal.get_registry_record(
            'open_pdf_in_a_new_window', interface=IGeverBumblebeeSettings)


@adapter(IOGMailMarker, Interface)
class BumblebeeMailOverlay(BumblebeeBaseDocumentOverlay):
    """Bumblebee overlay for base mails.
    """

    def is_latest_version(self):
        """Mails are not versionable."""
        return True

    def get_open_as_pdf_url(self):
        return u'{}/bumblebee-open-pdf?filename={}'.format(
            self.context.absolute_url(),
            quote(self._get_pdf_filename().encode('utf-8')))

    def get_checkout_url(self):
        return None

    def get_checkin_without_comment_url(self):
        return None

    def get_checkin_with_comment_url(self):
        return None

    def get_download_copy_link(self):
        href = u"{}/download?_authenticator={}".format(
            self.context.absolute_url(),
            self.context.restrictedTraverse('@@authenticator').token())

        return u'<a href="{}" class="{}">{}</a>'.format(
            href,
            'function-download-copy',
            translate('label_download_copy',
                      default="Download copy",
                      domain='opengever.document',
                      context=self.request))


@adapter(IDocumentSchema, IVersionedContextMarker)
class BumblebeeDocumentVersionOverlay(BumblebeeBaseDocumentOverlay):
    """Bumblebee overlay for versioned documents"""

    def is_latest_version(self):
        return self.version_id == self.context.get_current_version_id()

    def get_checkout_url(self):
        return None

    def get_open_as_pdf_url(self):
        return None

    def get_checkin_without_comment_url(self):
        return None

    def get_checkin_with_comment_url(self):
        return None

    def get_edit_metadata_url(self):
        return None

    def get_detail_view_url(self):
        return None

    def render_checked_out_viewlet(self):
        return ''

    def render_lock_info_viewlet(self):
        return ''


class BumblebeeOverlayBaseView(BrowserView, ActionButtonRendererMixin):
    """Baseview for the bumblebeeoverlay.
    """

    def __call__(self):
        if not is_bumblebee_feature_enabled():
            raise NotFound

        overlay_context = self.context
        version_id = self._get_version_id(overlay_context)

        if version_id is not None:
            overlay_context = self._retrieve_version(overlay_context, version_id)
            alsoProvides(self.request, IVersionedContextMarker)

        self.overlay = getMultiAdapter((overlay_context, self.request), IBumblebeeOverlay)
        self.overlay.version_id = version_id

        # we only render an html fragment, no reason to waste time on diazo
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return super(BumblebeeOverlayBaseView, self).__call__()

    def _get_version_id(self, context):
        version_id = self.request.get('version_id')

        if not version_id:
            return None

        if version_id.isdigit():
            return int(version_id)

        return NotFound

    def _retrieve_version(self, context, version_id):
        try:
            # CMFEditions causes writes to the parent when retrieving versions
            unprotected_write(aq_parent(context))
            return Versioner(context).retrieve(version_id)

        except ArchivistRetrieveError:
            # Version does not exists.
            raise NotFound


class BumblebeeOverlayListingView(BumblebeeOverlayBaseView):
    """Bumblebeeoverlay called from somewhere on the plone site.
    i.e. documents-tab, search-view, overview-tab
    """


class BumblebeeOverlayDocumentView(BumblebeeOverlayBaseView):
    """Bumblebeeoverlay called from the document itself.
    """

    is_on_detail_view = True
