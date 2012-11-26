from plone.app.search.browser import Search
from zope.component import getMultiAdapter


class OpengeverSearch(Search):
    """Customizing the plone default Search View.
    """

    def breadcrumbs(self, item):
        obj = item.getObject()
        view = getMultiAdapter((obj, self.request), name='breadcrumbs_view')
        # cut off the item itself
        breadcrumbs = list(view.breadcrumbs())[:-1]

        return breadcrumbs
