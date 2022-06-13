from opengever.base.source import RepositoryPathSourceBinder
from opengever.base.source import SolrObjPathSourceBinder
from opengever.dossier.base import DOSSIER_STATES_OPEN


sablon_template_source = SolrObjPathSourceBinder(
    portal_type=("opengever.meeting.sablontemplate"),
    navigation_tree_query={
        'object_provides':
            ['opengever.dossier.templatefolder.interfaces.ITemplateFolder',
             'opengever.meeting.sablontemplate.ISablonTemplate',
             ],
    }
)


proposal_template_source = SolrObjPathSourceBinder(
    portal_type=("opengever.meeting.proposaltemplate"),
    navigation_tree_query={
        'object_provides':
            ['opengever.dossier.templatefolder.interfaces.ITemplateFolder',
             'opengever.meeting.proposaltemplate.IProposalTemplate',
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


repository_folder_source = RepositoryPathSourceBinder(
    object_provides='opengever.repository.repositoryfolder.IRepositoryFolderSchema',
    review_state='repositoryfolder-state-active',
    navigation_tree_query={
        'object_provides': [
            'opengever.repository.repositoryroot.IRepositoryRoot',
            'opengever.repository.repositoryfolder.IRepositoryFolderSchema',
        ]
    }
)
