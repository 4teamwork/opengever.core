from ftw.bumblebee.mimetypes import is_mimetype_supported
from opengever.base.browser.helper import get_css_class
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.bumblebee import get_representation_url_by_object
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee.interfaces import IBumblebeeOverlay
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.ogds.base.actor import Actor
from plone import api
from plone.protect import createToken
from Products.Five import BrowserView
from zExceptions import NotFound
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import implements
import os


class BumblebeeBaseDocumentOverlay(object):
    """Bumblebee overlay for base documents.
    """
    implements(IBumblebeeOverlay)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_preview_pdf_url(self):
        return get_representation_url_by_object('preview', self.context)

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

        return '{}/edit'.format(self.context.absolute_url())

    def get_detail_view_url(self):
        return self.context.absolute_url()

    def get_file_title(self):
        return self.get_file().filename if self.has_file() else None

    def get_file_size(self):
        """Return the filesize in KB."""
        return self.get_file().getSize() / 1024 if self.has_file() else None

    def get_checkout_url(self):
        if not self.has_file() or not self._is_checkout_and_edit_available():
            return None

        return '{}/editing_document?_authenticator={}'.format(
            self.context.absolute_url(),
            createToken())

    def get_download_copy_link(self):
        # Because of cyclic dependencies, we can not import
        # DownloadConfirmationHelper in the top of the file.
        from opengever.document.browser.download import DownloadConfirmationHelper

        if not self.has_file():
            return None

        dc_helper = DownloadConfirmationHelper()
        return dc_helper.get_html_tag(
            self.context.absolute_url(),
            additional_classes=[''],
            include_token=True
            )

    def get_open_as_pdf_url(self):
        mimetypeitem = self.context.get_mimetype()
        if not mimetypeitem or not is_mimetype_supported(mimetypeitem[0]):
            return None

        return get_representation_url_by_object(
            'pdf', obj=self.context, filename=self._get_pdf_filename())

    def get_checkin_without_comment_url(self):
        if not self.has_file():
            return None
        return self._get_checkin_url(with_comment=False)

    def get_checkin_with_comment_url(self):
        if not self.has_file():
            return None
        return self._get_checkin_url(with_comment=True)

    def has_file(self):
        return bool(self.get_file())

    def get_file(self):
        if not hasattr(self, '_file'):
            has_file = hasattr(self.context, 'file') and self.context.file
            self._file = self.context.file if has_file else None
        return self._file

    def _get_pdf_filename(self):
        if not self.has_file():
            # Bumblebee will use a placeholder filename
            return None

        filename, extenstion = os.path.splitext(self.get_file().filename)
        return '{}.pdf'.format(filename)

    def _is_checkin_allowed(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        return manager.is_checkin_allowed()

    def _is_checkout_and_edit_available(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        userid = manager.get_checked_out_by()

        if not userid:
            return manager.is_checkout_allowed()
        return userid == api.user.get_current().getId()

    def _get_checkin_url(self, with_comment=False):
        if not self._is_checkin_allowed():
            return None

        if with_comment:
            checkin_view = '@@checkin_document'
        else:
            checkin_view = '@@checkin_without_comment'

        return "{}/{}?_authenticator={}".format(
            self.context.absolute_url(),
            checkin_view,
            createToken())


class BumblebeeMailOverlay(BumblebeeBaseDocumentOverlay):
    """Bumblebee overlay for base mails.
    """

    def get_open_as_pdf_url(self):
        return None

    def get_checkout_url(self):
        return None

    def get_checkin_without_comment_url(self):
        return None

    def get_checkin_with_comment_url(self):
        return None

    def get_download_copy_link(self):
        href = "{}/download?_authenticator={}".format(
            self.context.absolute_url(),
            self.context.restrictedTraverse('@@authenticator').token())

        return "<a href={}>{}</a>".format(href, translate(
            'label_download_copy',
            default="Download copy",
            domain='opengever.document',
            context=self.request))

    def get_file(self):
        if not hasattr(self, '_file'):
            has_file = hasattr(self.context, 'message') and self.context.message
            self._file = self.context.message if has_file else None
        return self._file


class BumblebeeOverlayBaseView(BrowserView):
    """Baseview for the bumblebeeoverlay.
    """

    on_detail_view = False
    overlay = None

    def __call__(self):
        if not is_bumblebee_feature_enabled():
            raise NotFound

        self.overlay = getMultiAdapter(
            (self.context, self.request), IBumblebeeOverlay)

        # we only render an html fragment, no reason to waste time on diazo
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return super(BumblebeeOverlayBaseView, self).__call__()


class BumblebeeOverlayListingView(BumblebeeOverlayBaseView):
    """Bumblebeeoverlay called from somewhere on the plone site.
    i.e. documents-tab, search-view, overview-tab
    """


class BumblebeeOverlayDocumentView(BumblebeeOverlayBaseView):
    """Bumblebeeoverlay called from the document itself.
    """

    on_detail_view = True
