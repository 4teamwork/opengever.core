from opengever.base.browser.helper import get_css_class
from plone.app.contentlisting.catalog import \
    CatalogContentListingObject as CoreListingObject
from zope.component import getMultiAdapter


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
        plone_view = getMultiAdapter((self, self.request), name=u'plone')
        return plone_view.cropText(self._brain.containing_dossier, 200)

    def CroppedTitle(self):
        plone_view = getMultiAdapter((self, self.request), name=u'plone')
        return plone_view.cropText(self.Title(), 200)

    def CroppedDescription(self):
        """The CroppedDescription method from the corelisting
        is not implemented yet."""

        plone_view = getMultiAdapter((self, self.request), name=u'plone')
        return plone_view.cropText(self.Description(), 400)
