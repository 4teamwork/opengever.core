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


class DossierPathSourceBinder(ObjPathSourceBinder):
    """A Special PathSourceBinder wich only search in the main Dossier
    of the actual context
    """

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
