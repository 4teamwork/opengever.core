from Acquisition import aq_parent
from opengever.base.browser.navigation import make_tree_by_url
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.repository.interfaces import IRepositoryFolder
from opengever.repository.repositoryfolder import REPOSITORY_FOLDER_STATE_INACTIVE
from opengever.repository.repositoryroot import IRepositoryRoot
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zExceptions import BadRequest
from zope.component import adapter
from zope.dottedname.resolve import resolve
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, IOpengeverBaseLayer)
class Navigation(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        root_interface = self.get_root_interface()
        content_interfaces = self.get_content_interfaces()

        if self.request.form.get('include_root'):
            content_interfaces.append(root_interface)

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
            roots = api.content.find(
                object_provides=root_interface.__identifier__)
            if roots:
                root = roots[0].getObject()
            else:
                # when on a teamraum deployment with no repository, no root
                # is found. As a temporary fix we return no navigation in these
                # cases.
                root = None
                return {'navigation': {}}

        result = {
            'navigation': {
                '@id': '{}/@navigation'.format(root.absolute_url()),
            },
        }
        if not expand:
            return result

        items = api.content.find(
            object_provides=content_interfaces,
            path='/'.join(root.getPhysicalPath()),
            sort_on='sortable_title',
        )

        nodes = map(self.brain_to_node, items)
        result['navigation']['tree'] = make_tree_by_url(nodes)

        return result

    def _lookup_iface_by_identifier(self, identifier):
        return resolve(identifier) if identifier else None

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

    def brain_to_node(self, brain):
        node = {
            '@type': brain.portal_type,
            'text': brain.Title,
            'description': brain.Description,
            'url': brain.getURL(),
            'uid': brain.UID,
            'active': brain.review_state != REPOSITORY_FOLDER_STATE_INACTIVE,
            'current': self.context.absolute_url() == brain.getURL(),
            'current_tree': self.context.absolute_url().startswith(brain.getURL()),
            'is_leafnode': None,
        }
        if brain.portal_type == 'opengever.repository.repositoryfolder':
            node['is_leafnode'] = not brain.has_sametype_children
        return node


class NavigationGet(Service):

    def reply(self):
        navigation = Navigation(self.context, self.request)
        return navigation(expand=True)['navigation']
