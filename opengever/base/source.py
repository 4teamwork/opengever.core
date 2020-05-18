from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from ftw.solr.query import make_query
from opengever.base import interfaces
from opengever.base import is_solr_feature_enabled
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.formwidget.contenttree.source import CustomFilter
from plone.formwidget.contenttree.source import ObjPathSource
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import getUtility
from zope.component import queryMultiAdapter


class SolrObjPathSource(ObjPathSource):
    """Custom ObjPathSource that supports searching in solr.

    Only search is switched to solr, the navtree queries are still querying
    the catalog, and so does CustomFilter. This is to not break CustomFilter
    which might be index based. Not sure how to port that to solr.

    """
    def __init__(self, context, selectable_filter, navigation_tree_query=None,
                 default=None, defaultFactory=None):

        if navigation_tree_query is not None:
            navigation_tree_query.update({
                'sort_on': navigation_tree_query.get('sort_on',
                                                     'sortable_title'),
            })

        super(SolrObjPathSource, self).__init__(
                context, selectable_filter,
                navigation_tree_query=navigation_tree_query,
                default=default,
                defaultFactory=defaultFactory)

        self.solr = getUtility(ISolrSearch)
        # Validate that filters are also usable with solr. Do so always and
        # not only when solr is enabled to catch incompatibilities early.
        self.make_solr_filters(self.navigation_tree_query)
        self.make_solr_filters(self.selectable_filter.criteria)

    def search(self, query, limit=20):
        """Search in solr (if the solr feature is enabled) but then convert
        solr results to brains and continue working with them.

        Brains are obtained using path/rid which is expected to be performant
        enough. Search results are usually limited to 10.
        """
        if not is_solr_feature_enabled():
            for each in super(SolrObjPathSource, self).search(query, limit=limit):
                yield each
            return

        results = self.solr.search(
            query=make_query(query),
            filters=self.make_solr_filters(self.selectable_filter.criteria),
            rows=limit,
            fl=['path'],
        )

        from opengever.base.solr import OGSolrContentListing  # XXX: FIXME!
        for solr_doc in OGSolrContentListing(results):
            brain = self._getBrainByToken(solr_doc.getPath())
            if brain:
                yield self.getTermByBrain(brain, real_value=False)

    def make_solr_filters(self, catalog_query):
        """Attempt to convert a catalog query to solr filters.

        This method currently only converts the subset of catalog queries
        that we actually use in the navigation_tree_query or the
        selectable_filter.
        """
        schema = self.solr.manager.schema
        filters = []
        for key, value in catalog_query.items():
            if key == 'SearchableText':
                continue
            if key not in schema.fields:
                continue

            # ftw.solr expect an exact match on the 'path' index,
            # so we have to use `path_parent`.
            if key == 'path':
                key = 'path_parent'

            if isinstance(value, dict):
                # range queries and depth limiting for path queryies are not an
                # use case so far so we lazily defer implementation until this
                # is necessary
                if 'range' in value:
                    raise NotImplementedError("Can't handle range queries.")
                if 'depth' in value:
                    raise NotImplementedError("Can't handle depth queries.")
                value = value.get('query')

            if isinstance(value, (list, tuple)):
                value = list(value)
            else:
                value = [value]

            for i, v in enumerate(value):
                if isinstance(v, str):
                    v = v.strip()
                    v = escape(v)
                    if ' ' in v:
                        v = '"%s"' % v
                elif isinstance(v, bool):
                    v = 'true' if v else 'false'
                value[i] = v
            if len(value) > 1:
                filters.append(u'%s:(%s)' % (key, ' OR '.join(value)))
            else:
                filters.append(u'%s:%s' % (key, value[0]))

        return filters


class SolrObjPathSourceBinder(ObjPathSourceBinder):
    path_source = SolrObjPathSource


class RepositoryPathSourceBinder(SolrObjPathSourceBinder):
    """A Special PathSourceBinder which searches this repository
    system.
    """

    def __call__(self, context):
        """Set the path to the repository root.
        """

        root_path = ''
        parent = context

        while not IPloneSiteRoot.providedBy(parent):
            if parent.portal_type == 'opengever.repository.repositoryroot':
                root_path = '/'.join(parent.getPhysicalPath())
                break
            else:
                parent = aq_parent(aq_inner(parent))

        if not root_path:
            root_path = '/'.join(parent.getPhysicalPath())

        if not self.navigation_tree_query:
            self.navigation_tree_query = {}

        if 'path' not in self.navigation_tree_query:
            self.navigation_tree_query['path'] = {}

        self.navigation_tree_query['path']['query'] = root_path
        # We also add the path filter to the selectable_filter as the
        # navigation_tree_query is not used when querying the source and
        # we need to only allow to query objects in the root_path.
        if "path" not in self.selectable_filter.criteria:
            self.selectable_filter.criteria['path'] = {}
        self.selectable_filter.criteria['path']['query'] = root_path

        modificator = queryMultiAdapter((
            context, context.REQUEST),
            interfaces.IRepositoryPathSourceBinderQueryModificator
        )
        if modificator:
            self.navigation_tree_query = modificator(
                self.navigation_tree_query)

        source = self.path_source(
            context,
            selectable_filter=self.selectable_filter,
            navigation_tree_query=self.navigation_tree_query)

        # The path source bases on the navtree strategy, which adds a
        # portal_type query option, which disables all types not-to-list
        # in the navigation. This is not a navigation - so remove this
        # limitation.
        del source.navigation_tree_query['portal_type']

        return source


class DossierPathSourceBinder(SolrObjPathSourceBinder):
    """A Special PathSourceBinder wich only search in the main Dossier
    of the actual context
    """

    def __init__(self, navigation_tree_query=None, filter_class=CustomFilter, **kw):
        self.selectable_filter = filter_class(**kw)
        self.navigation_tree_query = navigation_tree_query

    def __call__(self, context):
        """ gets main-dossier path and put it to the navigation_tree_query """
        dossier_path = ''
        parent = context
        while not IPloneSiteRoot.providedBy(parent) and \
                parent.portal_type != 'opengever.repository.repositoryfolder':
            dossier_path = '/'.join(parent.getPhysicalPath())
            parent = aq_parent(aq_inner(parent))
        if not self.navigation_tree_query:
            self.navigation_tree_query = {}

        self.navigation_tree_query['path'] = {'query': dossier_path}

        # Extend path in selectable_filter, to make sure only objects
        # inside the current dossier are selectable.
        self.selectable_filter.criteria['path'] = {'query': dossier_path}

        source = self.path_source(
            context,
            selectable_filter=self.selectable_filter,
            navigation_tree_query=self.navigation_tree_query)

        # The path source bases on the navtree strategy, which adds a
        # portal_type query option, which disables all types not-to-list
        # in the navigation. This is not a navigation - so remove this
        # limitation.
        del source.navigation_tree_query['portal_type']

        return source
