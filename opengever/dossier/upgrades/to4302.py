from ftw.upgrade import UpgradeStep


class ManageMeetingPermission(UpgradeStep):
    """Also manage meeting permission in dossier workflows.
    """

    def __call__(self):
        self.setup_install_profile('profile-opengever.dossier.upgrades:4302')

        self.update_workflow_security(
            ['opengever_dossier_workflow',
             'opengever_templatedossier_workflow'],
            reindex_security=False)
