from opengever.tabbedview.interfaces import IGeverCatalogTableSourceConfig
from opengever.tabbedview.interfaces import IGeverTableSourceConfig
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
import ftw.tabbedview.browser.listing


class ListingView(ftw.tabbedview.browser.listing.ListingView):
    """XXX OpenGever specific override of the ftw.tabbedview ListingView in
    order to fix batching by overriding the page template.
    """

    implements(IGeverTableSourceConfig)

    batching = ViewPageTemplateFile("batching.pt")
    template = ViewPageTemplateFile("generic.pt")

    def get_base_query(self):
        raise NotImplementedError()


class CatalogListingView(ftw.tabbedview.browser.listing.CatalogListingView):
    """XXX OpenGever specific override of the ftw.tabbedview
    CatalogListingView in order to fix batching by overriding
    the page template.
    """

    implements(IGeverCatalogTableSourceConfig)

    batching = ViewPageTemplateFile("batching.pt")
    template = ViewPageTemplateFile("generic.pt")
