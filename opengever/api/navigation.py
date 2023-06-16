from Acquisition import aq_parent
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_filters
from opengever.base.browser.navigation import make_tree_by_url
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.solr import OGSolrDocument
from opengever.repository.interfaces import IRepositoryFolder
from opengever.repository.repositoryfolder import REPOSITORY_FOLDER_STATE_INACTIVE
from opengever.repository.repositoryroot import IRepositoryRoot
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import getUtility
from zope.dottedname.resolve import resolve
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, IOpengeverBaseLayer)
class Navigation(object):

    FIELDS = [
        'UID',
        'path',
        'portal_type',
        'review_state',
        'Title',
        'title_de',
        'title_en',
        'title_fr',
        'Description',
        'filename',
        'has_sametype_children',
        'is_subdossier',
        'dossier_type',
    ]

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.solr = getUtility(ISolrSearch)

    def __call__(self, expand=False):
        root_interface = self.get_root_interface()
        content_interfaces = self.get_content_interfaces()

        if self.request.form.get('include_root'):
            content_interfaces.append(root_interface)

        result = {
            'navigation': {
                '@id': '{}/@navigation'.format(self.context.absolute_url()),
            },
        }

        if not expand:
            return result

        root = self.find_root(root_interface, content_interfaces)
        solr_docs = self.query_solr(root, content_interfaces)

        nodes = map(self.solr_doc_to_node, solr_docs)
        result['navigation']['tree'] = make_tree_by_url(nodes)

        return result

    def find_root(self, root_interface, content_interfaces):
        context = self.context

        if root_interface not in content_interfaces:
            while (not root_interface.providedBy(context)
                   and not IPloneSiteRoot.providedBy(context)):
                context = aq_parent(context)
        else:
            # This happens i.e. on lookup a dossier tree from a subdossier.
            #
            # The current context is the subdossier which is also
            # providing the root_interface. We have to get sure, that we return
            # the most upper object providing the given root_interface if
            # the root_interface is within `content_interfaces`
            current = context
            while (not IPloneSiteRoot.providedBy(current)):
                if root_interface.providedBy(current):
                    context = current
                current = aq_parent(current)

        if root_interface.providedBy(context):
            root = context
        else:
            response = self.solr.search(
                filters=make_filters(
                    object_provides=root_interface.__identifier__),
                sort='path asc',
                fl=["path"],
            )
            roots = [OGSolrDocument(d) for d in response.docs]

            if roots:
                root = roots[0].getObject()
            else:
                raise BadRequest("No root found for interface: {}".format(
                    root_interface.__identifier__))
        return root

    def query_solr(self, root, content_interfaces):
        query = {
            'object_provides': [i.__identifier__ for i in content_interfaces],
            'path_parent': '/'.join(root.getPhysicalPath()),
            'trashed': 'false',
        }

        review_states = self.request.form.get('review_state', [])
        if review_states:
            query['review_state'] = review_states

        filters = make_filters(**query)

        if self.request.form.get('include_context'):
            # Include context branch's UIDs in the query, by adding them as
            # a filter that is OR'ed with the main filters (which themselves
            # are AND'ed together). This is necessary because restrictions
            # from the main filters must not be applied to the context branch.
            context_uids = list(self.get_context_branch_uids(root))
            if context_uids:
                context_filter = make_filters(UID=context_uids)[0]
                main_filters = self._join_filters(make_filters(**query), 'AND')
                filters = self._join_filters([main_filters, context_filter], 'OR')

        resp = self.solr.search(
            filters=filters,
            sort='sortable_title asc',
            rows=10000,
            fl=self.FIELDS)

        return [OGSolrDocument(doc) for doc in resp.docs]

    def get_context_branch_uids(self, root):
        """Return UIDs of the current context's chain up to the root.
        """
        for item in self.context.aq_chain:
            item_uid = item.UID()
            if item_uid == root.UID():
                break
            yield item_uid

    def _lookup_iface_by_identifier(self, identifier):
        return resolve(identifier) if identifier else None

    def _join_filters(self, filters, op):
        op = ' %s ' % op
        return op.join(['(%s)' % flt for flt in filters])

    def get_root_interface(self):
        """Lookups the root_interface provided within the request parameter.

        This interface is used as the navigation root identifier.
        """
        interface = self.request.form.get('root_interface')
        try:
            return self._lookup_iface_by_identifier(
                interface) or IRepositoryRoot
        except ImportError:
            raise BadRequest("The provided `root_interface` could not be "
                             "looked up: {}".format(interface))

    def get_content_interfaces(self):
        """Lookups the content_interfaces provided within the request parameter.

        The interfaces provided in `content_interfaces` are used as navigation
        items.
        """
        interfaces = self.request.form.get('content_interfaces')
        if not interfaces:
            return [IRepositoryFolder]

        if not isinstance(interfaces, list):
            interfaces = [interfaces]

        content_interfaces = []
        for interface in interfaces:
            try:
                content_interfaces.append(
                    self._lookup_iface_by_identifier(interface))
            except ImportError:
                raise BadRequest("The provided `content_interfaces` could not be "
                                 "looked up: {}".format(interface))
        return content_interfaces

    def solr_doc_to_node(self, solr_doc):
        wrapper = IContentListingObject(solr_doc)
        context_url = self.context.absolute_url()

        node = {
            '@type': wrapper.portal_type,
            'text': wrapper.Title(),
            'description': wrapper.Description(),
            'url': wrapper.getURL(),
            'uid': wrapper.UID,
            'active': wrapper.review_state() != REPOSITORY_FOLDER_STATE_INACTIVE,
            'current': context_url == wrapper.getURL(),
            'current_tree': context_url.startswith(wrapper.getURL()),
            'is_leafnode': None,
            'is_subdossier': wrapper.is_subdossier,
            'review_state': wrapper.review_state(),
            'dossier_type': wrapper.dossier_type,
        }
        if wrapper.portal_type == 'opengever.repository.repositoryfolder':
            node['is_leafnode'] = not wrapper.has_sametype_children
        return json_compatible(node)


class NavigationGet(Service):

    def reply(self):
        navigation = Navigation(self.context, self.request)
        return navigation(expand=True)['navigation']
