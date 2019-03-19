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

        while (not root_interface.providedBy(context)
               and not IPloneSiteRoot.providedBy(context)):
            context = aq_parent(context)

        if root_interface.providedBy(context):
            root = context
        else:
            roots = api.content.find(
                object_provides=root_interface.__identifier__)
            if roots:
                root = roots[0].getObject()
            else:
                root = None

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
        interface = self.request.form.get('content_interfaces')
        try:
            content_interfaces = self._lookup_iface_by_identifier(
                interface) or IRepositoryFolder
        except ImportError:
            raise BadRequest("The provided `content_interfaces` could not be "
                             "looked up: {}".format(interface))

        return content_interfaces if isinstance(content_interfaces, list) \
            else [content_interfaces]

    def brain_to_node(self, brain):
        return {
            '@type': brain.portal_type,
            'text': brain.Title,
            'description': brain.Description,
            'url': brain.getURL(),
            'uid': brain.UID,
            'active': brain.review_state != REPOSITORY_FOLDER_STATE_INACTIVE,
            'current': self.context.absolute_url() == brain.getURL(),
            'current_tree': self.context.absolute_url().startswith(brain.getURL()),
        }


class NavigationGet(Service):

    def reply(self):
        navigation = Navigation(self.context, self.request)
        return navigation(expand=True)['navigation']
