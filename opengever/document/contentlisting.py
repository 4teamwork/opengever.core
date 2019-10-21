from ftw import bumblebee
from opengever.base.browser.helper import get_css_class
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.document.document import Document
from opengever.document.widgets.document_link import DocumentLinkWidget
from opengever.mail.mail import OGMail
from opengever.trash.trash import ITrashed
from plone import api
from plone.app.contentlisting.realobject import RealContentListingObject
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest


class DocumentContentListingObject(RealContentListingObject):

    @property
    def is_document(self):
        return True

    @property
    def is_trashed(self):
        return self._realobject.is_trashed

    @property
    def is_removed(self):
        removed_states = [Document.removed_state, OGMail.removed_state]
        return api.content.get_state(self) in removed_states

    def ContentTypeClass(self):
        """Return the css class for the MIME type of the document's file.
        """
        return get_css_class(self._realobject)

    def is_bumblebeeable(self):
        return is_bumblebee_feature_enabled()

    def render_link(self, **kwargs):
        return DocumentLinkWidget(self).render(**kwargs)

    def get_breadcrumbs(self):
        breadcrumbs_view = getMultiAdapter((self._realobject, getRequest()),
                                           name='breadcrumbs_view')
        return breadcrumbs_view.breadcrumbs()

    def get_overlay_url(self):
        """Return the url to fetch the bumblebee overlay."""

        if not self.is_bumblebeeable():
            return None

        return '{}/@@bumblebee-overlay-listing'.format(self.getURL())

    def preview_image_url(self):
        """Return the url to fetch the bumblebee preview thumbnail."""

        if not self.is_bumblebeeable():
            return None

        return bumblebee.get_service_v3().get_representation_url(
            self._realobject, 'thumbnail')

    def get_overlay_title(self):
        return self.Title().decode('utf-8')
