from ftw.upgrade import UpgradeStep
from plone import api


MEMBERSFOLDER_ID = 'private'


class InstallOpengeverPrivate(UpgradeStep):
    """Install opengever private.
    """

    def __call__(self):
        self.install_upgrade_profile()
        mtool = api.portal.get_tool('portal_membership')
        mtool.setMembersFolderById(MEMBERSFOLDER_ID)
        mtool.setMemberAreaType('opengever.private.folder')
        if not api.portal.get().get(MEMBERSFOLDER_ID):
            self.create_private_root()

    def create_private_root(self):
        private_root = api.content.create(
            type='opengever.private.root',
            title='Private',
            container=api.portal.get())

        if private_root.id != MEMBERSFOLDER_ID:
            api.content.rename(obj=private_root, new_id=MEMBERSFOLDER_ID)
