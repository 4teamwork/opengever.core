from opengever.base.monkey.patching import MonkeyPatch


class PatchOFSRoleManager(MonkeyPatch):

    def __call__(self):
        def manage_setLocalRoles(manager, userid, roles, REQUEST=None, **kwargs):
            if 'Owner' not in roles and not kwargs.get('verified'):
                raise ValueError('This permission change is not verified '
                                 'by RoleAssignmentManager.')

            return original_manage_setLocalRoles(manager, userid, roles)

        def manage_delLocalRoles(manager, userids, REQUEST=None, **kwargs):
            if not kwargs.get('verified'):
                raise ValueError('This permission change is not verified '
                                 'by RoleAssignmentManager.')
            return original_manage_delLocalRoles(manager, userids)

        def manage_addLocalRoles(manager, userid, roles, REQUEST=None, **kwargs):
            if 'Owner' not in roles and not kwargs.get('verified'):
                raise ValueError('This permission change is not verified '
                                 'by RoleAssignmentManager.')

            return original_manage_addLocalRoles(manager, userid, roles)

        from OFS.role import RoleManager
        locals()['__patch_refs__'] = False
        original_manage_setLocalRoles = RoleManager.manage_setLocalRoles
        original_manage_delLocalRoles = RoleManager.manage_delLocalRoles
        original_manage_addLocalRoles = RoleManager.manage_addLocalRoles

        self.patch_refs(RoleManager, 'manage_setLocalRoles', manage_setLocalRoles)
        self.patch_refs(RoleManager, 'manage_delLocalRoles', manage_delLocalRoles)
        self.patch_refs(RoleManager, 'manage_addLocalRoles', manage_addLocalRoles)
