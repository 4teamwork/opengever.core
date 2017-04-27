from ftw.upgrade import UpgradeStep


class UpdateProposalWorkflow(UpgradeStep):
    """Update proposal workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(['opengever_proposal_workflow'],
                                      reindex_security=False)
