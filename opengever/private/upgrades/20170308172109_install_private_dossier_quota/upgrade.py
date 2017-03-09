from ftw.upgrade import UpgradeStep
from opengever.quota.sizequota import ISizeQuota


class InstallPrivateDossierQuota(UpgradeStep):
    """Install private dossier quota.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.index_new_behaviors()
        self.calculate_private_folder_usage()

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

    def calculate_private_folder_usage(self):
        msg = 'Calculate usage in private folders.'
        for obj in self.objects({'portal_type': ['opengever.private.folder']},
                                msg):
            ISizeQuota(obj).recalculate()
