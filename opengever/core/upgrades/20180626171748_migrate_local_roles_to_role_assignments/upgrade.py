from ftw.upgrade import UpgradeStep
from opengever.base.role_assignments import ASSIGNNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager


class MigrateLocalRolesToRoleAssignments(UpgradeStep):
    """Migrate local roles to roleAssignments.
    """

    def __call__(self):
        self.install_upgrade_profile()
        msg = 'Migrate local roles to roleAssignments'
        query = {}

        for obj in self.objects(query, msg):
            self.add_role_assignments(obj)

    def add_role_assignments(self, obj):
        storage = RoleAssignmentManager(obj).storage
        for principal, roles in obj.get_local_roles():
            storage.add_or_update(
                principal, roles, ASSIGNNMENT_VIA_SHARING, None)
