from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.oguid import Oguid
from opengever.base.utils import get_preferred_language_code
from opengever.core.upgrade import SQLUpgradeStep
from sqlalchemy import and_
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


proposals_table = table(
    'proposals',
    column('id'),
    column('repository_folder_title'),
    column('int_id'),
    column('admin_unit_id'),
)


class UpdateRepositoryFolderTitle(SQLUpgradeStep):
    """With the upgradestep 4632 the column repository_folder_title was
    introduced and filled with a placeholder. This upgradestep now replaces
    the placeholders with the correct value.

    """
    def migrate(self):
        query = {'portal_type': 'opengever.meeting.proposal'}
        for proposal in self.objects(query, 'Update dossier_reference_number'):
            oguid = Oguid.for_object(proposal)
            repository_folder_title = self.get_repo_folder_title(proposal)

            self.execute(proposals_table.update().values(
                repository_folder_title=repository_folder_title).where(
                and_(
                    proposals_table.columns.int_id == oguid.int_id,
                    proposals_table.columns.admin_unit_id == oguid.admin_unit_id,
                )))

    def get_repo_folder_title(self, proposal):
        main_dossier = aq_parent(aq_inner(proposal)).get_main_dossier()
        repo_folder = aq_parent(aq_inner(main_dossier))
        return repo_folder.Title(language=get_preferred_language_code(),
                                 prefix_with_reference_number=False)
