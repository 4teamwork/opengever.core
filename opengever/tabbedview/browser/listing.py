from ftw.tabbedview.browser.listing import \
    ListingView as FtwTabbedviewListingView
from ftw.tabbedview.browser.listing import \
    CatalogListingView as FtwTabbedviewCatalogListingView
from zope.app.pagetemplate import ViewPageTemplateFile


class ListingView(FtwTabbedviewListingView):
    """ XXX OpenGever specific override of the ftw.tabbedview ListingView in
    order to fix batching by overriding the page template.
    """

    batching = ViewPageTemplateFile("batching.pt")


class CatalogListingView(FtwTabbedviewCatalogListingView):
    """ XXX OpenGever specific override of the ftw.tabbedview
    CatalogListingView in order to fix batching by overriding
    the page template.
    """

    batching = ViewPageTemplateFile("batching.pt")
