from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot
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
        the SearchableText.

        XXX This method should be removed, after the solr integration"""

        request = self.request
        text = query.get('SearchableText', None)
        if text is None:
            text = request.form.get('SearchableText', '')

        catalog = getToolByName(self.context, 'portal_catalog')
        valid_keys = self.valid_keys + tuple(catalog.indexes())

        for k, v in request.form.items():
            if v and ((k in valid_keys) or k.startswith('facet.')):

                if isinstance(v, list):
                    v = {'query': (DateTime(v[0]), DateTime(v[1])),
                         'range': 'min:max'}
                query[k] = v

        if text:
            query['SearchableText'] = quote_chars(text)

        # don't filter on created at all if we want all results
        created = query.get('created')
        if created:
            if created.get('query'):
                if created['query'][0] <= EVER:
                    del query['created']

        # respect `types_not_searched` setting
        types = query.get('portal_type', [])
        if 'query' in types:
            types = types['query']
        query['portal_type'] = self.filter_types(types)
        # respect effective/expiration date
        query['show_inactive'] = False
        # respect navigation root
        if 'path' not in query:
            query['path'] = getNavigationRoot(self.context)

        return query
