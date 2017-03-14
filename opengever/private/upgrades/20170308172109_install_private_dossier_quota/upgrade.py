from ftw.upgrade import UpgradeStep


class InstallPrivateDossierQuota(UpgradeStep):
    """Install private dossier quota.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.index_new_behaviors()
        self.configure_error_log()

        # recalculation was moved to upgrade
        # 20170314200202_fix_private_folder_usage_calculation
        # because it had errors.

    def index_new_behaviors(self):
        msg = 'Update `object_provides` for objects with new behavior.'
        catalog = self.getToolByName('portal_catalog')

        for obj in self.objects({'portal_type': ['ftw.mail.mail',
                                                 'opengever.document.document',
                                                 'opengever.private.folder']},
                                msg):
            catalog.reindexObject(obj,
                                  idxs=['object_provides'],
                                  update_metadata=False)

    def configure_error_log(self):
        error_log = self.getToolByName('error_log')
        properties = error_log.getProperties()
        if 'ForbiddenByQuota' in properties.get('ignored_exceptions', ()):
            return

        properties['ignored_exceptions'] += ('ForbiddenByQuota',)
        error_log.setProperties(**properties)
