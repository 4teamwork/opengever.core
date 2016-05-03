from five import grok
from ftw.bumblebee.interfaces import IBumblebeeable
from opengever.base.browser.helper import get_css_class
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.bumblebee import get_representation_url_by_object
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.ogds.base.actor import Actor
from plone import api
from plone.protect import createToken
from zExceptions import NotFound
from zope.component import getAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter


class BumblebeeOverlayMixin(object):
    """Provides all methods to display all the necessary metadata and actions
    on the overlay.
    """

    def __call__(self):
        if not is_bumblebee_feature_enabled():
            raise NotFound

        return super(BumblebeeOverlayMixin, self).__call__()

    def get_preview_pdf_url(self):
        return get_representation_url_by_object('preview', self.context)

    def get_mime_type_css_class(self):
        return get_css_class(self.context)

    def get_file_title(self):
        file_ = self.context.file
        return file_ and file_.filename

    def get_file_size(self):
        file_ = self.context.file
        return file_ and self.context.file.size / 1024

    def get_creator_link(self):
        return Actor.user(self.context.Creator()).get_link()

    def get_document_date(self):
        return api.portal.get_localized_time(
            str(self.context.document_date), long_format=True)

    def get_containing_dossier(self):
        return self.context.get_parent_dossier()

    def get_sequence_number(self):
        return getUtility(ISequenceNumber).get_number(self.context)

    def get_reference_number(self):
        return getAdapter(self.context, IReferenceNumber).get_number()

    def get_checkout_url(self):
        if not self.context.file or not self._is_checkout_and_edit_available():
            return None

        return '{}/editing_document?_authenticator={}'.format(
            self.context.absolute_url(),
            createToken())

    def get_download_copy_link(self):
        # Because of cyclic dependencies, we can not import
        # DownloadConfirmationHelper in the top of the file.
        from opengever.document.browser.download import DownloadConfirmationHelper

        if not self.context.file:
            return None

        dc_helper = DownloadConfirmationHelper()
        return dc_helper.get_html_tag(
            self.context.absolute_url(),
            additional_classes=[''],
            include_token=True
            )

    def get_edit_metadata_url(self):
        if not api.user.has_permission(
                'Modify portal content', obj=self.context):
            return None

        return '{}/edit'.format(self.context.absolute_url())

    def get_detail_view_url(self):
        return self.context.absolute_url()

    def get_checkin_without_comment_url(self):
        return self._get_checkin_url(with_comment=False)

    def get_checkin_with_comment_url(self):
        return self._get_checkin_url(with_comment=True)

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

        checkin_view = '@@checkin_document'
        if with_comment:
            checkin_view = '@@checkin_without_comment'

        return "{}/{}?_authenticator={}".format(
            self.context.absolute_url(),
            checkin_view,
            createToken())

    def _is_checkin_allowed(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        return manager.is_checkin_allowed()


class BumblebeeOverlayListing(BumblebeeOverlayMixin, grok.View):
    grok.context(IBumblebeeable)
    grok.require('zope2.View')
    grok.name('bumblebee-overlay-listing')
    grok.template('bumblebeeoverlayview')


class BumblebeeOverlayDocument(BumblebeeOverlayMixin, grok.View):
    grok.context(IBumblebeeable)
    grok.require('zope2.View')
    grok.name('bumblebee-overlay-document')
    grok.template('bumblebeeoverlayview')

    def get_detail_view_url(self):
        return None
