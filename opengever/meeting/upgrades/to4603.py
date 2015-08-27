from ftw.upgrade import UpgradeStep
from opengever.base.interfaces import IReferenceNumber
from Acquisition import aq_inner
from Acquisition import aq_parent

class UpdateProposalDossierReferenceNumber(UpgradeStep):
    """With the upgradestep 4602 the column dossier_reference_number was
    introduced and filled with a placeholder. This upgradestep now replaces
    the placeholders with the correct value."""

    def __call__(self):
        query = {'portal_type': 'opengever.meeting.proposal'}
        for proposal in self.objects(query, 'Update dossier_reference_number'):
            model = proposal.load_model()
            model.dossier_reference_number = self.get_reference_number(proposal)

    def get_reference_number(self, proposal):
        main_dossier = aq_parent(aq_inner(proposal)).get_main_dossier()
        return IReferenceNumber(main_dossier).get_number()
