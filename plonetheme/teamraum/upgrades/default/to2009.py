from ftw.upgrade import UpgradeStep
from plonetheme.teamraum.hooks import remove_screen_media_types


class RemoveScreenMediaType(UpgradeStep):

    def __call__(self):
        remove_screen_media_types(self.portal)
