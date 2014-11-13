from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.portlets.tree import treeportlet
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import classProvides
from zope.interface import implements


class AssignRepoRootNavigation(object):
    """Assigns the repository root navigation the plone site for the first
    repository root encountered in the pipeline.

    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.has_assigned_portlet = False

    def __iter__(self):
        for item in self.previous:
            if item.get('_type') == 'opengever.repository.repositoryroot':
                if not self.has_assigned_portlet:
                    self.has_assigned_portlet = True
                    repository_id = item['_repo_root_id']
                    assign_repo_root_portlets(self.context, repository_id)

            yield item


def assign_repo_root_portlets(site, repo_root_id):
    assign_tree_portlet(context=site, root_path=repo_root_id,
                        remove_nav=True, block_inheritance=False)


def assign_tree_portlet(context, root_path, remove_nav=False,
                        block_inheritance=False):
    # Assign tree portlet to given context
    manager = getUtility(
        IPortletManager, name=u'plone.leftcolumn', context=context)
    mapping = getMultiAdapter((context, manager,), IPortletAssignmentMapping)
    if 'opengever-portlets-tree-TreePortlet' not in mapping.keys():
        mapping['opengever-portlets-tree-TreePortlet'] = \
            treeportlet.Assignment(root_path=root_path)

    if remove_nav:
        # Remove unused navigation portlet
        if 'navigation' in mapping.keys():
            del mapping[u'navigation']

    if block_inheritance:
        # Block inherited context portlets
        assignable = getMultiAdapter(
            (context, manager), ILocalPortletAssignmentManager)
        assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)
