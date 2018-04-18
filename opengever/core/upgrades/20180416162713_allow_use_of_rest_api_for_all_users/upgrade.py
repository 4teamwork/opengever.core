from ftw.upgrade import UpgradeStep
from plone import api


class AllowUseOfRESTAPIForAllUsers(UpgradeStep):
    """Allow use of REST API for all users.
    """

    def __call__(self):
        self.install_upgrade_profile()

        self.remove_api_user_role()

    def remove_api_user_role(site):
        """Remove the APIUser role, which is no longer used.
        """

        uf = api.portal.get_tool('acl_users')

        # Remove global role assignments
        role_manager = uf.portal_role_manager
        if 'APIUser' in role_manager._roles:
            role_manager.removeRole('APIUser')

        # Remove the role from the site root __ac_roles__
        api.portal.get()._delRoles(['APIUser'])
