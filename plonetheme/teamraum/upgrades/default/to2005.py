from ftw.upgrade import UpgradeStep


class Upgrades(UpgradeStep):
    """Upgrades to 2005.

    Import mimetypes
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-collective.mtrsetup:default')
        self.setup_install_profile(
            'profile-plonetheme.teamraum.upgrades.default:2005')

        cat = self.portal.portal_catalog
        for obj in self.objects({'portal_type': 'File'},
                                'update getIcon metadata'):
            cat.reindexObject(obj, idxs=['Title'], update_metadata=True)
