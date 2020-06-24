from AccessControl import getSecurityManager
from Acquisition import aq_inner
from opengever.base.utils import get_preferred_language_code
from opengever.repository.repositoryfolder import REPOSITORY_FOLDER_STATE_INACTIVE
from pkg_resources import get_distribution
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.navigation import CatalogNavigationTabs
from Products.CMFPlone.browser.navigation import get_view_url
from Products.Five import BrowserView
from zope.component import getMultiAdapter
import json
import os.path


def make_tree_by_url(nodes, url_key='url', children_key='nodes'):
    """Creates a nested tree of nodes from a flat list-like object of nodes.
    Each node is expected to be a dict with a url-like string stored
    under the ``url_key``.
    Each node will end up with a ``children_key``, containing a list
    of children nodes.
    The nodes are changed in place, be sure to make copies first when
    necessary.
    """

    for node in nodes:
        node[children_key] = []

    nodes_by_url = dict((node[url_key], node) for node in nodes)
    root = []

    for node in nodes:
        parent_url = os.path.dirname(node[url_key])
        if parent_url in nodes_by_url:
            nodes_by_url[parent_url][children_key].append(node)
        else:
            root.append(node)

    return root


class JSONNavigation(BrowserView):

    def __call__(self):
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')

        if self.request.get('cache_key'):
            # Only cache when there is a cache_key in the request.
            # Representations may be cached by any cache.
            # The cached representation is to be considered fresh for 1 year
            # http://stackoverflow.com/a/3001556/880628
            response.setHeader('Cache-Control', 'private, max-age=31536000')

        return self.json()

    def get_caching_url(self):
        url = self.context.absolute_url() + '/navigation.json'
        params = []
        cache_key = self._navigation_cache_key()
        if cache_key:
            params.append('cache_key={0}'.format(cache_key))

        if self.request.getHeader('Cache-Control') == 'no-cache':
            params.append('nocache=true')

        params.append('language={}'.format(get_preferred_language_code()))

        if params:
            url = '{0}?{1}'.format(url, '&'.join(params))

        return url

    def json(self):
        return json.dumps(self._tree())

    def query(self):
        interfaces = (
            'opengever.repository.repositoryfolder.IRepositoryFolderSchema',
        )
        return {'object_provides': interfaces,
                'path': '/'.join(self.context.getPhysicalPath()),
                'sort_on': 'sortable_title'}

    def _tree(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(self.query())
        nodes = map(self._brain_to_node, brains)
        return make_tree_by_url(nodes)

    def _brain_to_node(self, brain):
        return {'text': brain.Title,
                'description': brain.Description,
                'url': brain.getURL(),
                'uid': brain.UID,
                'active': brain.review_state != REPOSITORY_FOLDER_STATE_INACTIVE, }

    def _navigation_cache_key(self):
        last_modified = self._get_newest_modification_timestamp()
        if last_modified is not None:
            version = get_distribution('opengever.core').version
            username = getSecurityManager().getUser().getId()
            return '-'.join((version, last_modified, username))
        else:
            return None

    def _get_newest_modification_timestamp(self):
        """Returns the timestamp (in milliseconds) of the latest modification
        that happened to any object in the navigation.

        The problem here is that the ``modified`` index's precision is minutes.
        This means that when multiple objects are modified in the same minute,
        the order of a modified-ordered query may be wrong.

        We therefore must make sure that we consider enough brains in order to
        be sure that the timestamp is really accurate.

        This was previously implemented with a separate modified_seconds index,
        which turned out to be a bad idea (conflict errors, performance).
        """

        query = self.query()
        # Also include repository root:
        query['object_provides'] += (
            'opengever.repository.repositoryroot.IRepositoryRoot',
        )
        query['sort_on'] = 'modified'
        query['sort_order'] = 'reverse'
        query['sort_limit'] = 100

        brains = getToolByName(self.context, 'portal_catalog')(query)
        if len(brains) == 0:
            return None

        # Walk through the brains as long as the brain's modification
        # timestamp is in the same minute; that is the set of brains
        # which the modified-index of the catalog cannot order correctly.
        # When we reach the next minute, return the newest modification
        # timestamp.

        def minute_of(stamp):
            return stamp.strftime('%Y-%m-%d %H:%M')

        previous = None
        newest = None
        for brain in brains:
            newest = max(brain.modified, newest)
            if previous and minute_of(previous) != minute_of(brain.modified):
                break
            previous = brain.modified

        return str(newest.millis())


class CustomizedCatalogNavigationTabs(CatalogNavigationTabs):
    """
    Plone's default implementation requires the `getRemoteUrl` metadata from the
    catalog. As we removed this metadata, we need a custom implementation that
    does not depend on it and thus doesn't support external links.
    """

    def topLevelTabs(self, actions=None, category='portal_tabs'):
        context = aq_inner(self.context)

        portal_properties = getToolByName(context, 'portal_properties')
        self.navtree_properties = getattr(portal_properties,
                                          'navtree_properties')
        self.site_properties = getattr(portal_properties,
                                       'site_properties')
        self.portal_catalog = getToolByName(context, 'portal_catalog')

        if actions is None:
            context_state = getMultiAdapter((context, self.request),
                                            name=u'plone_context_state')
            actions = context_state.actions(category)

        # Build result dict
        result = []
        # first the actions
        if actions is not None:
            for actionInfo in actions:
                data = actionInfo.copy()
                data['name'] = data['title']
                result.append(data)

        # check whether we only want actions
        if self.site_properties.getProperty('disable_folder_sections', False):
            return result

        query = self._getNavQuery()

        rawresult = self.portal_catalog.searchResults(query)

        # now add the content to results
        idsNotToList = self.navtree_properties.getProperty('idsNotToList', ())
        for item in rawresult:
            if not (item.getId in idsNotToList or item.exclude_from_nav):
                id, item_url = get_view_url(item)
                data = {'name': utils.pretty_title_or_id(context, item),
                        'id': item.getId,
                        'url': item_url,
                        'description': item.Description}
                result.append(data)

        return result
