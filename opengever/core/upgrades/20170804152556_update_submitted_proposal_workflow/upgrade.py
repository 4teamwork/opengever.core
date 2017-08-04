from ftw.upgrade import UpgradeStep


class UpdateSubmittedProposalWorkflow(UpgradeStep):
    """Update submitted proposal workflow: let CommitteeGroupMember edit documents.

    For the word-meeting-feature it is important that committee group members are
    able to checkout and edit the proposal-documents (which are located in the
    proposal).
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(['opengever_submitted_proposal_workflow'],
                                      reindex_security=False)
