from Acquisition import aq_base
from ftw import bumblebee
from Missing import Value as MissingValue
from opengever.base.browser.helper import get_css_class
from opengever.base.helpers import display_name
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee import is_bumblebeeable
from opengever.document.document import Document
from opengever.document.widgets.document_link import DocumentLinkWidget
from opengever.mail.mail import OGMail
from plone.app.contentlisting.catalog import CatalogContentListingObject
from plone.app.contentlisting.realobject import RealContentListingObject
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.i18n import translate


class OpengeverCatalogContentListingObject(CatalogContentListingObject):
    """OpenGever specific catalog content listing.
    Provides correct MIME type icons and containing dossier for rendering
    breadcrumbs in search results. Additionaly it provides cropped Title and
    Description methods.
    """

    simple_link_template = ViewPageTemplateFile('templates/simple_link.pt')
    documentish_types = ['opengever.document.document', 'ftw.mail.mail']

    def __getattr__(self, name):
        """
        The original CatalogContentListingObject drops the aquistion
        information, when getting the attribute from the object.
        This lead to problems when accessing is_subdossier for example.

        Customization can be removed as soon the bug gets fixed in
        plone.app.contentlisting.
        """

        if name.startswith('_'):
            raise AttributeError(name)
        if hasattr(aq_base(self._brain), name):
            return getattr(self._brain, name)
        elif hasattr(aq_base(self.getObject()), name):
            # Here we diverge from CatalogContentListingObject which
            # returns getattr(aq_base(self.getObject()), name)
            return getattr(self.getObject(), name)
        else:
            raise AttributeError(name)

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

        return "state-{}".format(self.review_state())

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
            self.getDataOrigin(), 'thumbnail')

    def get_preview_frame_url(self):
        """Return the url to fetch the bumblebee preview HTML frame."""
        if not self.is_bumblebeeable():
            return None

        return bumblebee.get_service_v3().get_representation_url(
            self.getDataOrigin(), 'preview')

    def preview_pdf_url(self):
        """Return the url to fetch the bumblebee preview pdf."""
        if not self.is_bumblebeeable():
            return None

        return bumblebee.get_service_v3().get_representation_url(
            self.getDataOrigin(), 'pdf')

    def get_overlay_title(self):
        """Return the title for the bumblebee overlay."""

        if not self.is_bumblebeeable():
            return None

        return self.CroppedTitle().decode('utf-8')

    def get_breadcrumbs(self):
        obj = self._brain.getObject()
        breadcrumbs_view = getMultiAdapter((obj, obj.REQUEST),
                                           name='breadcrumbs_view')
        return breadcrumbs_view.breadcrumbs()

    def is_bumblebeeable(self):
        if not hasattr(self, '_is_bumblebeeable'):
            self._is_bumblebeeable = (
                is_bumblebee_feature_enabled() and is_bumblebeeable(self))

        return self._is_bumblebeeable

    def render_link(self):
        if self.is_documentish:
            return DocumentLinkWidget(self).render()

        return self._render_simplelink()

    def translated_review_state(self):
        review_state = self.review_state()
        if review_state:
            return translate(
                review_state, domain='plone', context=self.request)

    def responsible_fullname(self):
        return display_name(self._brain.responsible)

    def issuer_fullname(self):
        return display_name(self._brain.issuer)

    def checked_out_fullname(self):
        return display_name(self._brain.checked_out)

    def creator(self):
        return self._brain.Creator

    def reference_number(self):
        return self._brain.reference

    def mimetype(self):
        return self._brain.getContentType

    def _render_simplelink(self):
        self.context = self
        return self.simple_link_template(self, self.request)


class OpengeverRealContentListingObject(RealContentListingObject):

    def __getattr__(self, name):
        """The original RealContentListingObject drops the aquistion
        information, when accessing the value. This lead to problems when
        calling getOwner in the Title accessor for example.

        Customization can be removed as soon the bug gets fixed in
        plone.app.contentlisting.
        """
        if name.startswith('_'):
            raise AttributeError(name)
        obj = self.getObject()
        if hasattr(aq_base(obj), name):
            return getattr(obj, name)
        else:
            raise AttributeError(name)

    def translated_review_state(self):
        return translate(
            self.review_state(), domain='plone', context=self.request)
