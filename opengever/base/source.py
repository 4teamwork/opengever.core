from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.referencewidget.sources import ReferenceObjSourceBinder
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.formwidget.contenttree.source import CustomFilter
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot


# Allow traversable on the whole active repo tree and open dossiers
DEFAULT_TRAVERSABLE_PARAMS = {
    'start': 'parent',
    'traversal_query': {'object_provides': [
        'opengever.repository.repositoryroot.IRepositoryRoot',
        'opengever.repository.repositoryfolder.IRepositoryFolderSchema',
        'opengever.dossier.behaviors.dossier.IDossierMarker',
    ],
        'review_state': [
            'dossier-state-active',
            'repositoryfolder-state-active',
            'repositoryroot-state-active']
    }
}


# Allow only traversable on the repo tree and dossiers
DOSSIER_TRAVERSABLE_PARAMS = {
    'start': 'parent',
    'traversal_query': {
        'object_provides': [
            'opengever.repository.repositoryroot.IRepositoryRoot',
            'opengever.repository.repositoryfolder.IRepositoryFolderSchema',
            'opengever.dossier.behaviors.dossier.IDossierMarker',
        ]
    }
}


def get_root_path(context):
    root_path = ''
    parent = context
    while not IPloneSiteRoot.providedBy(parent):
        if parent.portal_type == 'opengever.repository.repositoryroot':
            root_path = '/'.join(parent.getPhysicalPath())
            break
        else:
            parent = aq_parent(aq_inner(parent))

    return root_path


class RepositoryPathSourceBinder(ReferenceObjSourceBinder):

    def __init__(self, *args, **kwargs):
        super(RepositoryPathSourceBinder, self).__init__(*args, **kwargs)
        self.root_path = get_root_path


class DossierPathSourceBinder(ObjPathSourceBinder):
    """A Special PathSourceBinder wich only search in the main Dossier
    of the actual context
    """

    def __init__(self, navigation_tree_query=None, filter_class=CustomFilter, **kw):
        self.selectable_filter = filter_class(**kw)
        self.navigation_tree_query = navigation_tree_query

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

        # Extend path in selectable_filter, to make sure only objects
        # inside the current dossier are selectable.
        self.selectable_filter.criteria['path'] = {'query': dossier_path}

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
