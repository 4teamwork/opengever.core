from opengever.base.browser.helper import get_css_class
from plone.app.contentlisting.catalog import CatalogContentListingObject as CoreListingObject


class OpengeverCatalogContentListingObject(CoreListingObject):
    """OpenGever specific catalog content listing.
    Provides correct MIME type icons and containing dossier for rendering
    breadcrumbs in search results.
    """

    def ContentTypeClass(self):
        """Here we set the correct content type class so that documents with
        files have the correct MIME type icons displayed.
        """
        return get_css_class(self._brain)

    def getIcon(self):
        """Because we use CSS sprites for icons, we don't return an icon here.
        """
        return None

    def containing_dossier(self):
        """Used for rendering breadcrumbs in search results.
        """
        return self._brain.containing_dossier
