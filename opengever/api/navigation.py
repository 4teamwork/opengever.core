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
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, IOpengeverBaseLayer)
class Navigation(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        context = self.context
        while (not IRepositoryRoot.providedBy(context)
               and not IPloneSiteRoot.providedBy(context)):
            context = aq_parent(context)

        if IRepositoryRoot.providedBy(context):
            root = context
        else:
            roots = api.content.find(
                object_provides=IRepositoryRoot.__identifier__)
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
            object_provides=IRepositoryFolder.__identifier__,
            path='/'.join(root.getPhysicalPath()),
            sort_on='sortable_title',
        )

        nodes = map(self.brain_to_node, items)
        result['navigation']['tree'] = make_tree_by_url(nodes)

        return result

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
