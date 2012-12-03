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

    def filter_query(self, query):
        """The filter query of the standard search view (plone.app.search)
        cancel the query generation if not SearchableText is given.
        In some case (for example in opengever.advancedsearch), we generate
        also searches without a searchabletext. So we temporarily fake
        the SearchableText."""

        if not self.request.form.get('SearchableText', None):
            self.request.form['SearchableText'] = 'temporary fake text'
            query = super(OpengeverSearch, self).filter_query(query)
            query['SearchableText'] = ''
            return query

        return super(OpengeverSearch, self).filter_query(query)
