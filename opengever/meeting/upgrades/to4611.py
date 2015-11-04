from ftw.upgrade import UpgradeStep


class UpdateWorkflowWithCustomRole(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.meeting.upgrades:4611')

        self.update_workflow_security(
            ['opengever_committee_workflow'],
            reindex_security=True)
