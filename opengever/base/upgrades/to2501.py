from ftw.upgrade import UpgradeStep


class InitOGAdvancedSearchProfileVersion(UpgradeStep):

    def __call__(self):
        profileid = 'opengever.advancedsearch:default'
        if self.portal_setup.getLastVersionForProfile(profileid) == 'unknown':
            # Initialize it
            self.portal_setup.setLastVersionForProfile(profileid, '0')
