from plone.formwidget.contenttree import ObjPathSourceBinder
from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot


class RepositoryPathSourceBinder(ObjPathSourceBinder):
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

        if not self.navigation_tree_query:
            self.navigation_tree_query = {}

        if 'path' not in self.navigation_tree_query:
            self.navigation_tree_query['path'] = {}

        self.navigation_tree_query['path']['query'] = root_path

        return self.path_source(
            context,
            selectable_filter=self.selectable_filter,
            navigation_tree_query=self.navigation_tree_query)


class DossierPathSourceBinder(ObjPathSourceBinder):
    """A Special PathSourceBinder wich only search in the main Dossier
    of the actual context
    """

    def __call__(self, context):
        """ gets main-dossier path and put it to the navigation_tree_query """
        dossier_path = ''
        parent = context
        while not IPloneSiteRoot.providedBy(parent) and \
                parent.portal_type != 'opengever.repository.repositoryroot':
            dossier_path = '/'.join(parent.getPhysicalPath())
            parent = aq_parent(aq_inner(parent))
        if not self.navigation_tree_query:
            self.navigation_tree_query = {}
        self.navigation_tree_query['path'] = {'query': dossier_path}

        return self.path_source(
            context,
            selectable_filter=self.selectable_filter,
            navigation_tree_query=self.navigation_tree_query)
