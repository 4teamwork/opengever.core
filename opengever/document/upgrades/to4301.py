from ftw.upgrade import UpgradeStep


class DropOwner(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-opengever.document.upgrades:4301')
        self.update_workflow_security(['opengever_document_workflow'])
