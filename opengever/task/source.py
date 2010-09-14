from plone.formwidget.contenttree import ObjPathSourceBinder
from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot


class DossierPathSourceBinder(ObjPathSourceBinder):
    """A Special PathSourceBinder wich only search in the main Dossier
    of the actual context
    """

    def __call__(self, context):
        """ gets main-dossier path and put it to the navigation_tree_query """
        dossier_path = ''
        parent = context
        while not IPloneSiteRoot.providedBy(parent) and \
                parent.Type() != 'RepositoryFolder':
            dossier_path = '/'.join(parent.getPhysicalPath())
            parent = aq_parent(aq_inner(parent))

        self.navigation_tree_query['path'] = dossier_path
        return self.path_source(
            context,
            selectable_filter=self.selectable_filter,
            navigation_tree_query=self.navigation_tree_query)
