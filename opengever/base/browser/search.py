from DateTime import DateTime
from ftw.bumblebee.utils import get_representation_url_by_brain
from opengever.bumblebee import is_bumblebee_feature_enabled
from plone import api
from plone.app.search.browser import EVER
from plone.app.search.browser import quote_chars
from plone.app.search.browser import Search
from Products.CMFPlone.browser.navtree import getNavigationRoot
from zope.component import getMultiAdapter


FILTER_TYPES = [
    'ftw.mail.mail',
    'opengever.document.document',
    'opengever.dossier.businesscasedossier',
    'opengever.inbox.forwarding',
    'opengever.task.task']


class OpengeverSearch(Search):
    """Customizing the plone default Search View.
    """

    def __init__(self, context, request):
        super(OpengeverSearch, self).__init__(context, request)

        catalog = api.portal.get_tool('portal_catalog')
        self.valid_keys = self.valid_keys + tuple(catalog.indexes())

    def results(self, query=None, batch=True, b_size=10, b_start=0):
        """Overwrite this method to adjust the default batch size from
        10 to 25.
        """
        b_size = 25
        return super(OpengeverSearch, self).results(
            query=query, batch=batch, b_size=b_size, b_start=b_start)

    def breadcrumbs(self, item):
        obj = item.getObject()
        view = getMultiAdapter((obj, self.request), name='breadcrumbs_view')
        # cut off the item itself
        breadcrumbs = list(view.breadcrumbs())[:-1]

        return breadcrumbs

    def types_list(self):
        types = super(OpengeverSearch, self).types_list()
        return list(set(FILTER_TYPES) & set(types))

    def should_handle_key(self, key):
        return ((key in self.valid_keys) or key.startswith('facet.')) \
            and not key.endswith('_usage')

    def handle_query_filter_value(self, query, key, value):
        if not value or not self.should_handle_key(key):
            return

        usage = self.request.form.get('{}_usage'.format(key))
        if usage:
            self.handle_date_query_filter_value(usage, query, key, value)
        else:
            query[key] = value

    def handle_date_query_filter_value(self, usage, query, key, value):
        if usage not in ('min', 'max', 'minmax'):
            return
        if usage == 'minmax' and len(value) == 2:
            query_value = [DateTime(value[0]), DateTime(value[1])]
        else:
            query_value = [DateTime(value[0])]
        query[key] = {
            'query': query_value,
            'range': usage
        }

    def is_bumblebee_feature_enabled(self):
        return is_bumblebee_feature_enabled()

    def get_preview_image_url(self, brain):
        if not brain.bumblebee_checksum:
            return None

        return get_representation_url_by_brain('thumbnail', brain)

    def filter_query(self, query):
        """The filter query of the standard search view (plone.app.search)
        cancel the query generation if not SearchableText is given.
        In some case (for example in opengever.advancedsearch), we generate
        also searches without a searchabletext. So we temporarily fake
        the SearchableText.

        XXX This method should be removed, after the solr integration
        meta-XXX should it? now it contains custom stuff.

        """
        request = self.request
        text = query.get('SearchableText', None)
        if text is None:
            text = request.form.get('SearchableText', '')

        for key, value in request.form.items():
            self.handle_query_filter_value(query, key, value)

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

    def get_overlay_url(self, item):
        return '{}/@@bumblebee-overlay-listing'.format(item.getURL())
