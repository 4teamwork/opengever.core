from Products.CMFCore.utils import getToolByName
import os


class Treeify(object):
    """ Generates a tree structure out of a set of catalog brains incl. all
        parents.

        Example: Give is the <mybrain instance4>

        >>> {'children': [
        ...    {'group_roles': [],
        ...     'item': <mybrain instance1>,
        ...     'user_roles': '',
        ...     'children': [
        ...         {'group_roles': [],
        ...          'item': <mybrain instance2>,
        ...          'user_roles': '',
        ...          'children': [
        ...              {'group_roles': [],
        ...               'item': <mybrain instance3>,
        ...               'user_roles': '',
        ...               'children': [
        ...                   {'group_roles': [],
        ...                    'item': <mybrain instance4>,
        ...                    'user_roles': u'Can view',
        ...                    'children': []}]}]}]}]}
    """

    def __init__(self, brains, root_path, callback):
        self._brains = brains
        self._root_path = root_path
        self._callback = callback
        self._brains_by_path = {}
        self._nodes_by_path = {}
        self.context = None

    def __call__(self, context):
        self.context = context
        self._load_brain_cache()
        for brain in self._brains:
            self._update_node(brain.getPath())
        return self._nodes_by_path[self._root_path]

    def _load_brain_cache(self):
        for brain in self._brains:
            self._brains_by_path[brain.getPath()] = brain

    def _get_node(self, path):
        if path not in self._nodes_by_path:
            self._update_node(path)
        return self._nodes_by_path[path]

    def _update_node(self, path):
        if path in self._nodes_by_path:
            return

        node = {'children': []}

        site_root_path = '/'.join(
            getToolByName(self.context,
                          'portal_url').getPortalObject().getPhysicalPath())
        if path == site_root_path:
            self._nodes_by_path[path] = node
        else:
            brain = self._get_brain(path)
            node = {'children': []}
            self._callback(brain, node)
            self._nodes_by_path[path] = node

        if path != self._root_path:
            parent_path = os.path.dirname(path)
            self._get_node(parent_path)['children'].append(node)

    def _get_brain(self, path):
        if path not in self._brains_by_path:
            catalog = getToolByName(self.context, 'portal_catalog')
            self._brains_by_path[path] = catalog.unrestrictedSearchResults(
                {'path': {'query': path, 'depth': 0}})[0]
        return self._brains_by_path[path]
