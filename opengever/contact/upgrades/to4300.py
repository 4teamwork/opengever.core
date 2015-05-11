from ftw.upgrade import UpgradeStep


class DropOwner(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-opengever.contact.upgrades:4300')
        self.update_workflow_security(['opengever_contact_workflow'],
                                      reindex_security=False)
