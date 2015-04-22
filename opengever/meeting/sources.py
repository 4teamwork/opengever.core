from plone.formwidget.contenttree import ObjPathSourceBinder
from opengever.base.source import RepositoryPathSourceBinder
from opengever.dossier.base import DOSSIER_STATES_OPEN


sablon_template_source = ObjPathSourceBinder(
    portal_type=("opengever.meeting.sablontemplate"),
    navigation_tree_query={
        'object_provides':
            ['opengever.dossier.templatedossier.interfaces.ITemplateDossier',
             'opengever.meeting.sablontemplate.ISablonTemplate',
             ],
        }
)


all_open_dossiers_source = RepositoryPathSourceBinder(
    object_provides='opengever.dossier.behaviors.dossier.IDossierMarker',
    review_state=DOSSIER_STATES_OPEN,
    navigation_tree_query={
        'object_provides': [
            'opengever.repository.repositoryroot.IRepositoryRoot',
            'opengever.repository.repositoryfolder.'
            'IRepositoryFolderSchema',
            'opengever.dossier.behaviors.dossier.IDossierMarker',
            ],
        'review_state': [
            'repositoryroot-state-active',
            'repositoryfolder-state-active'] + DOSSIER_STATES_OPEN,
    }
)
