from ftw.upgrade import UpgradeStep


class AddPermissionsToWorkflows(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.meeting.upgrades:4607')

        self.update_workflow_security(
            ['opengever_committeecontainer_workflow',
             'opengever_committee_workflow'],
            reindex_security=True)
