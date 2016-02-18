from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.interfaces import IReferenceNumber
from opengever.base.oguid import Oguid
from opengever.core.upgrade import SQLUpgradeStep
from sqlalchemy import and_
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


proposals_table = table(
    'proposals',
    column('id'),
    column('dossier_reference_number'),
    column('int_id'),
    column('admin_unit_id'),
)


class UpdateProposalDossierReferenceNumber(SQLUpgradeStep):
    """With the upgradestep 4602 the column dossier_reference_number was
    introduced and filled with a placeholder. This upgradestep now replaces
    the placeholders with the correct value."""

    def migrate(self):
        query = {'portal_type': 'opengever.meeting.proposal'}
        for proposal in self.objects(query, 'Update dossier_reference_number'):
            oguid = Oguid.for_object(proposal)
            dossier_reference_number = self.get_reference_number(proposal)

            self.execute(proposals_table.update().values(
                dossier_reference_number=dossier_reference_number).where(
                and_(
                    proposals_table.columns.int_id == oguid.int_id,
                    proposals_table.columns.admin_unit_id == oguid.admin_unit_id,
                )))

    def get_reference_number(self, proposal):
        main_dossier = aq_parent(aq_inner(proposal)).get_main_dossier()
        return IReferenceNumber(main_dossier).get_number()
