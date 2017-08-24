from ftw.upgrade import UpgradeStep


class MigrateCommitteeContainerRoles(UpgradeStep):
    """Migrate committee container roles.

    We map the roles as follows:

    Contributor -> CommitteeAdministrator
    Reader -> MeetingUser

    Editor is usually assigned in combination with Contributor. The new
    role-concept for opengever.meeting has no equivalent for Editor so we
    don't look at that assignment during migration.

    """
    def __call__(self):
        self.install_upgrade_profile()
        self.migrate_container_roles()

    def migrate_container_roles(self):
        query = {'portal_type': 'opengever.meeting.committeecontainer'}
        for container in self.objects(
                query, 'update committee-container local roles'):

            for principal, assigned_roles in container.get_local_roles():
                new_roles = set(assigned_roles) - set(
                    ['Reader', 'Contributor', 'Editor'])

                if 'Reader' in assigned_roles:
                    new_roles.add('MeetingUser')
                if 'Contributor' in assigned_roles:
                    new_roles.add('CommitteeAdministrator')

                container.manage_setLocalRoles(principal, list(new_roles))
            container.reindexObjectSecurity()
