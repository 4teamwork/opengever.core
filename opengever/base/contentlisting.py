from ftw import bumblebee
from Missing import Value as MissingValue
from opengever.base.browser.helper import get_css_class
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee import is_bumblebeeable
from opengever.document.document import Document
from opengever.document.renderer import DocumentLinkRenderer
from opengever.mail.mail import OGMail
from plone.app.contentlisting.catalog import CatalogContentListingObject
from zope.component import getMultiAdapter


class OpengeverCatalogContentListingObject(CatalogContentListingObject):
    """OpenGever specific catalog content listing.
    Provides correct MIME type icons and containing dossier for rendering
    breadcrumbs in search results. Additionaly it provides cropped Title and
    Description methods.
    """

    documentish_types = ['opengever.document.document', 'ftw.mail.mail']

    @property
    def is_document(self):
        return self._brain.portal_type == 'opengever.document.document'

    @property
    def is_documentish(self):
        return self._brain.portal_type in self.documentish_types

    @property
    def is_trashed(self):
        return self._brain.trashed

    @property
    def is_removed(self):
        removed_states = [Document.removed_state, OGMail.removed_state]
        return self.review_state() in removed_states

    def ContentTypeClass(self):
        """Here we set the correct content type class so that documents with
        files have the correct MIME type icons displayed.
        """
        return get_css_class(self._brain)

    def getIcon(self):
        """Because we use CSS sprites for icons, we don't return an icon here.
        """
        return None

    def _crop_text(self, text, length):
        if not text or text == MissingValue:
            return ''

        plone_view = getMultiAdapter((self, self.request), name=u'plone')
        return plone_view.cropText(text, length)

    def containing_dossier(self):
        """Returns the the title of the containing_dossier cropped to 200
        characters."""

        return self._crop_text(self._brain.containing_dossier, 200)

    def main_dossier_link(self):
        return '{}/redirect_to_main_dossier'.format(self.getURL())

    def CroppedTitle(self):
        """Returns the title cropped to 200 characters"""

        return self._crop_text(self.Title(), 200)

    def CroppedDescription(self):
        """The CroppedDescription method from the corelisting
        is not implemented yet."""

        return self._crop_text(self.Description(), 400)

    def get_css_classes(self):
        """Return the css classes for this item."""

        classes = ["state-{}".format(self.review_state())]
        if self.is_bumblebeeable():
            classes.append("showroom-item")
        return " ".join(classes)

    def get_overlay_url(self):
        """Return the url to fetch the bumblebee overlay."""

        if not self.is_bumblebeeable():
            return None

        return '{}/@@bumblebee-overlay-listing'.format(self.getURL())

    def get_preview_image_url(self):
        """Return the url to fetch the bumblebee preview thumbnail."""
        if not self.is_bumblebeeable():
            return None

        return bumblebee.get_service_v3().get_representation_url(
            self.getDataOrigin(), 'thumbnail')

    def get_overlay_title(self):
        """Return the title for the bumblebee overlay."""

        if not self.is_bumblebeeable():
            return None

        return self.CroppedTitle().decode('utf-8')

    def get_breadcrumbs(self):
        breadcrumbs = self._brain.breadcrumb_titles
        return " > ".join(
            [breadcrumb.get('Title') for breadcrumb in breadcrumbs])

    def is_bumblebeeable(self):
        if not hasattr(self, '_is_bumblebeeable'):
            self._is_bumblebeeable = (is_bumblebee_feature_enabled() and
                                      is_bumblebeeable(self))
        return self._is_bumblebeeable

    def render_link(self):
        if self.is_documentish:
            return DocumentLinkRenderer(self).render()

        structure = '<a href="{url}" alt="{title}" class="{css_class}">{title}</a>'
        return structure.format(
            url=self.getURL(), title=self.Title(),
            css_class=self.get_css_classes())
