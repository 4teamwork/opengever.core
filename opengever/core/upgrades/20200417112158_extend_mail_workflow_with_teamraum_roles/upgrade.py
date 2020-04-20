from ftw.upgrade import UpgradeStep


class ExtendMailWorkflowWithTeamraumRoles(UpgradeStep):
    """Extend mail workflow with teamraum roles.
    """

    def __call__(self):
        self.install_upgrade_profile()
        workspaces_path = '{}/workspaces'.format(
            '/'.join(self.portal.getPhysicalPath()))

        for obj in self.objects({
                'portal_type': 'ftw.mail.mail',
                'path': {'query': workspaces_path}},
                'Update permissions for teamraum mails'):

            self.update_security(obj, reindex_security=True)
