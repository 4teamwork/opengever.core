from plone.app.contentlisting.catalog import CatalogContentListingObject as CoreListingObject
from opengever.base.browser.helper import get_css_class


class OpengeverCatalogContentListingObject(CoreListingObject):

    def ContentTypeClass(self):
        """GEVER SPECIFIG"""
        return get_css_class(self._brain)

    def getIcon(self):
        return None

    def containing_dossier(self):

        return self._brain.containing_dossier
