from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyWorkflowSecurityUpdater


class EnableEditRisProposalInSubmittedAndScheduleState(UpgradeStep):
    """Enable Edit Ris  Proposal In Submitted /  State.
    """

    def __call__(self):
        self.install_upgrade_profile()
        with NightlyWorkflowSecurityUpdater(reindex_security=False) as updater:
            updater.update(
                ['opengever_ris_proposal_workflow'])
