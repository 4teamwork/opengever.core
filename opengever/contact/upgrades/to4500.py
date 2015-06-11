from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.translated_title import ITranslatedTitle


class ActivateTranslatedTitle(UpgradeStep):
    """Add ITranslatedTitle behavior to contactfolder.
    """

    def __call__(self):
        self.setup_install_profile('profile-opengever.contact.upgrades:4500')

        query = {'portal_type': ['opengever.contact.contactfolder']}
        msg = 'Migrate title of contactfolders'
        for inbox in self.objects(query, msg, savepoints=500):
            self.migrate_titles(inbox)

    def migrate_titles(self, obj):
        ITranslatedTitle(obj).title_de = obj.title
        obj.reindexObject()
