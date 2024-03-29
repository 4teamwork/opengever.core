from Acquisition import aq_parent
from ftw import bumblebee
from ftw.bumblebee.interfaces import IBumblebeeDocument
from opengever.base.browser.helper import get_css_class
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.base.protect import unprotected_write
from opengever.base.utils import to_html_xweb_intelligent
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee.interfaces import IBumblebeeOverlay
from opengever.bumblebee.interfaces import IVersionedContextMarker
from opengever.document import _ as document_mf
from opengever.document.browser.actionbuttons import VisibleActionButtonRendererMixin
from opengever.document.checkout.viewlets import DocumentStatusMessageViewlet
from opengever.document.document import IDocumentSchema
from opengever.document.versioner import Versioner
from opengever.locking.info import GeverLockInfoViewlet
from opengever.mail import _ as mail_mf
from opengever.mail.mail import IOGMailMarker
from opengever.ogds.base.actor import Actor
from opengever.trash.trash import ITrashed
from plone import api
from Products.CMFEditions.interfaces.IArchivist import ArchivistRetrieveError
from Products.Five import BrowserView
from zExceptions import NotFound
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface


@implementer(IBumblebeeOverlay)
@adapter(IDocumentSchema, Interface)
class BumblebeeBaseDocumentOverlay(object):
    """Bumblebee overlay for base documents.
    """

    version_id = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def trash_warning(self):
        if ITrashed.providedBy(self.context):
            return document_mf(
                u'warning_trashed', default=u'This document is trashed.',)

    def get_checkin_comment(self):
        version_id = self.version_id
        if version_id is None:
            version_id = getattr(self.context, 'version_id', None)
        if version_id is not None:
            version_metadata = Versioner(self.context).get_version_metadata(version_id)
            return version_metadata['sys_metadata']['comment']
        return u''

    def is_latest_version(self):
        """A documentish without versions is always the latest version."""
        return True

    def is_open_as_pdf_action_visible(self):
        return True

    def preview_pdf_url(self):
        return bumblebee.get_service_v3().get_representation_url(
            self.context, 'preview')

    def get_bumblebee_checksum(self):
        return IBumblebeeDocument(self.context).get_checksum()

    def get_mime_type_css_class(self):
        return get_css_class(self.context)

    def get_creator_link(self):
        return Actor.user(self.context.Creator()).get_link()

    def get_document_date(self):
        document_date = self.context.document_date
        if not document_date:
            return None
        return api.portal.get_localized_time(document_date)

    def get_containing_dossier(self):
        return self.context.get_parent_dossier()

    def get_sequence_number(self):
        return getUtility(ISequenceNumber).get_number(self.context)

    def get_reference_number(self):
        return getAdapter(self.context, IReferenceNumber).get_number()

    def get_title(self):
        return self.context.title

    def get_description(self):
        return to_html_xweb_intelligent(self.context.description)

    def has_file(self):
        return self.context.has_file()

    def get_file(self):
        return self.context.get_file()

    def get_file_size(self):
        """Return the filesize in KB."""
        return self.get_file().getSize() / 1024 if self.has_file() else None

    def get_filename(self):
        return self.get_file().filename if self.has_file() else None

    def render_document_status_viewlet(self):
        viewlet = DocumentStatusMessageViewlet(self.context, self.request, None, None)
        viewlet.update()
        return viewlet.render()

    def render_lock_info_viewlet(self):
        viewlet = GeverLockInfoViewlet(self.context, self.request, None, None)
        viewlet.update()
        return viewlet.render()


@adapter(IOGMailMarker, Interface)
class BumblebeeMailOverlay(BumblebeeBaseDocumentOverlay):
    """Bumblebee overlay for base mails.
    """

    def trash_warning(self):
        if ITrashed.providedBy(self.context):
            return mail_mf(
                u'warning_trashed', default=u'This mail is trashed.',)

    def is_latest_version(self):
        """Mails are not versionable."""
        return True


@adapter(IDocumentSchema, IVersionedContextMarker)
class BumblebeeDocumentVersionOverlay(BumblebeeBaseDocumentOverlay):
    """Bumblebee overlay for versioned documents"""

    def trash_warning(self):
        if self.trashed:
            return document_mf(
                u'warning_trashed', default=u'This document is trashed.',)

    def is_latest_version(self):
        return self.version_id == self.context.get_current_version_id()

    def is_open_as_pdf_action_visible(self):
        return False

    def render_document_status_viewlet(self):
        return ''

    def render_lock_info_viewlet(self):
        return ''


class BumblebeeOverlayBaseView(BrowserView, VisibleActionButtonRendererMixin):
    """Baseview for the bumblebeeoverlay.
    """

    def is_open_as_pdf_action_visible(self):
        return (
            self.is_open_as_pdf_action_available()
            and self.overlay.is_open_as_pdf_action_visible())

    def __call__(self):
        if not is_bumblebee_feature_enabled():
            raise NotFound

        overlay_context = self.context
        version_id = self._get_version_id(overlay_context)
        trashed = ITrashed.providedBy(overlay_context)

        if version_id is not None:
            overlay_context = self._retrieve_version(overlay_context, version_id)
            alsoProvides(self.request, IVersionedContextMarker)

        self.overlay = getMultiAdapter((overlay_context, self.request), IBumblebeeOverlay)
        self.overlay.version_id = version_id
        self.overlay.trashed = trashed

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

    def is_detail_view_link_visible(self):
        return True


class BumblebeeOverlayDocumentView(BumblebeeOverlayBaseView):
    """Bumblebeeoverlay called from the document itself.
    """
