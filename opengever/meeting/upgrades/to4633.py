from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.upgrade import UpgradeStep
from opengever.base.utils import get_preferred_language_code


class UpdateRepositoryFolderTitle(UpgradeStep):
    """With the upgradestep 4632 the column repository_folder_title was
    introduced and filled with a placeholder. This upgradestep now replaces
    the placeholders with the correct value.

    """
    def __call__(self):
        query = {'portal_type': 'opengever.meeting.proposal'}
        for proposal in self.objects(query, 'Update repository_folder_title'):
            model = proposal.load_model()
            model.repository_folder_title = self.get_repo_folder_title(proposal)

    def get_repo_folder_title(self, proposal):
        main_dossier = aq_parent(aq_inner(proposal)).get_main_dossier()
        repo_folder = aq_parent(aq_inner(main_dossier))
        return repo_folder.Title(language=get_preferred_language_code(),
                                 prefix_with_reference_number=False)
