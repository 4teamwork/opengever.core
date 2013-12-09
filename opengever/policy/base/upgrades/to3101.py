from ftw.upgrade import UpgradeStep
from Products.CMFCore.utils import getToolByName


class SetInitialProfileVersionForOGDSBase(UpgradeStep):
    """Set initial profile version for og.ogds.base:default"""

    def __call__(self):
        set_profile_version(self.portal, 'opengever.ogds.base:default', '1')


def set_profile_version(context, profile_id, version):
    """Set the DB version for a particular profile.
    """

    if profile_id.startswith('profile-'):
        raise Exception("Please specify the profile_id WITHOUT "
                        "the 'profile-' prefix!")

    ps = getToolByName(context, 'portal_setup')
    if not len(profile_id.split(':')) == 2:
        raise Exception("Invalid profile id '%s'" % profile_id)
    ps.setLastVersionForProfile(profile_id, unicode(version))
    assert(ps.getLastVersionForProfile(profile_id) == (version, ))
    print "Set version for '%s' to '%s'." % (profile_id, version)
    return [version]