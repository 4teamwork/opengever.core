from ftw.upgrade import UpgradeStep


class FixLocalRolesStringType(UpgradeStep):
    """Fix local roles string type.
    """

    def __call__(self):
        needs_reindex = False
        for obj in self.objects({'portal_type': 'opengever.meeting.committee'},
                                'Fix local roles string type'):
            for principal, roles in obj.get_local_roles():
                if isinstance(principal, unicode):
                    principal = principal.encode('utf8')
                    obj.manage_delLocalRoles([principal])
                    obj.manage_setLocalRoles(principal, list(roles))
                    needs_reindex = True

        if needs_reindex:
            catalog = self.getToolByName('portal_catalog')
            catalog.clearIndex('allowedRolesAndUsers')
            self.catalog_rebuild_index('allowedRolesAndUsers')
