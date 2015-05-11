from ftw.upgrade import UpgradeStep


class DropOwner(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-opengever.dossier.upgrades:4304')
        self.update_workflow_security(
            ['opengever_dossier_workflow',
             'opengever_templatedossier_workflow'])
