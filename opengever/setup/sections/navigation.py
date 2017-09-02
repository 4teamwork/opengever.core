from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import traverse
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
    """Assigns appropriate navigation tree portlets.

    - For the Plone Site:
        If there isn't one already, assign a tree portlet with the first
        repository root encountered in the pipeline (assumed to be the
        primary repo)

    - For (all) repository roots in the pipeline:
        Assign tree portlets with their respective location as the root.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.has_assigned_primary_portlet = False

    def _get_repo_root_id(self, item, portal):
        if '_repo_root_id' in item:
            # Classic og.setup
            return item['_repo_root_id']
        else:
            # OGGBundle import
            obj = traverse(portal, item['_path'])
            return obj.id

    def __iter__(self):
        portal = self.context
        for item in self.previous:
            if item.get('_type') == 'opengever.repository.repositoryroot':
                repository_id = self._get_repo_root_id(item, portal)
                if repository_id is not None:
                    # Plone Site
                    if not self.has_assigned_primary_portlet:
                        assign_repo_root_portlets(portal, repository_id)
                        self.has_assigned_primary_portlet = True

                    # Repo root
                    obj = traverse(portal, item['_path'])
                    assign_tree_portlet(
                        context=obj, root_path=repository_id,
                        remove_nav=True, block_inheritance=True)

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
