from plone.formwidget.contenttree import ObjPathSourceBinder
from Acquisition import aq_inner, aq_parent


class DossierPathSourceBinder(ObjPathSourceBinder):
    """A Special PathSourceBinder wich only search in the main Dossier
    of the actual context
    """

    def __call__(self, context):
        """ gets main-dossier path and put it to the navigation_tree_query """
        current = context = aq_inner(context)
        while aq_parent(current).Type() != 'RepositoryFolder':
            current = aq_parent(current)
        self.navigation_tree_query['path'] = '/'.join(
            current.getPhysicalPath())
        return self.path_source(
            context,
            selectable_filter=self.selectable_filter,
            navigation_tree_query=self.navigation_tree_query)
