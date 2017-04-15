from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.browser.helper import get_css_class
from opengever.base.pdfconverter import is_pdfconverter_enabled
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.inbox.inbox import IInbox
from opengever.task.task import ITask
from plone import api
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.dexterity.content import Item
from plone.locking.interfaces import IRefreshableLockable
from plone.protect import createToken
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.common import MimeTypeException
from zope.component import queryMultiAdapter

import logging


LOG = logging.getLogger('opengever.document')


class BaseDocumentMixin(object):
    """Abstract base class for document-ish content types."""

    removed_state = None
    active_state = None

    remove_transition = None
    restore_transition = None

    on_detail_view = False
    overlay = None

    def css_class(self):
        return get_css_class(self)

    def has_file(self):
        return bool(self.get_file())

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

    def is_checked_out_by_current_user(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)
        if manager is None:
            # This is probably a mail
            return False

        checkout = manager.get_checked_out_by()
        if checkout and checkout == api.user.get_current().getId():
            return True

        return False

    def is_edit_metadata_available(self):
        if self.is_versioned():
            return False

        if self.context.is_checked_out():
            return False

        if IRefreshableLockable(self.context).locked():
            return False

        return not IContentListingObject(self.context).is_trashed

    def is_versioned(self):
        return self.request.get('version_id') is not None

    def get_file(self):
        if not hasattr(self, '_file'):
            has_file = hasattr(self.context, 'file') and self.context.file
            self._file = self.context.file if has_file else None
        return self._file

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

    def get_download_copy_tag(self):
        dc_helper = DownloadConfirmationHelper()
        return dc_helper.get_html_tag(
            self.context.absolute_url(),
            additional_classes=['function-download-copy'],
            include_token=True,
            )

    def get_url(self):
        return self.context.absolute_url()

    def get_parent_dossier(self):
        """Return the document's parent dossier.

        A parent dossier is available for documents in a dossier/subdossier
        or for documents in a task.

        No parent dossier is available for documents in an inbox, in a
        forwarding or inside a proposal. In that case this method returns None.

        """
        parent = aq_parent(aq_inner(self))
        if (IDossierMarker.providedBy(parent)
                or IDossierTemplateMarker.providedBy(parent)):
            return parent
        if ITask.providedBy(parent):
            return parent.get_containing_dossier()

        return None

    def get_parent_inbox(self):
        """Return the document's parent inbox or None."""
        parent = aq_parent(aq_inner(self))
        if IInbox.providedBy(parent):
            return parent

        return None

    @property
    def is_removed(self):
        return api.content.get_state(obj=self) == self.removed_state

    def related_items(self):
        raise NotImplementedError

    def checked_out_by(self):
        raise NotImplementedError

    def get_current_version(self):
        raise NotImplementedError

    def get_filename(self):
        raise NotImplementedError

    def surrender(self, relative_to_portal=1):
        return Item.getIcon(self, relative_to_portal=relative_to_portal)

    def get_mimetype_icon(self, relative_to_portal=1):
        """Calculate the icon using the mime type of the file
        """
        utool = getToolByName(self, 'portal_url')

        mimetypeitem = self.get_mimetype()
        if not mimetypeitem:
            return self.surrender(relative_to_portal)

        icon = mimetypeitem[0].icon_path

        if relative_to_portal:
            return icon
        else:
            # Relative to REQUEST['BASEPATH1']
            res = utool(relative=1) + '/' + icon
            while res[:1] == '/':
                res = res[1:]
            return res

    def get_mimetype(self):
        """Return the mimetype as object. If there is no matching mimetype,
        it returns False.
        """
        mtr = getToolByName(self, 'mimetypes_registry', None)

        field = self.file
        if not field or not field.getSize():
            # there is no file
            return False

        # get icon by content type
        contenttype = field.contentType
        mimetypeitem = None
        try:
            mimetypeitem = mtr.lookup(contenttype)
        except MimeTypeException, msg:
            LOG.error(
                'MimeTypeException for %s. Error is: %s' % (
                    self.absolute_url(), str(msg)))
        if not mimetypeitem:
            # not found
            return False
        return mimetypeitem
