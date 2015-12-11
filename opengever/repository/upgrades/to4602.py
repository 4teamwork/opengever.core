from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.translated_title import ITranslatedTitle


class TranslatedTitleForRepositoryFolders(UpgradeStep):

    portal_type = 'opengever.repository.repositoryfolder'

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.repository.upgrades:4602')

        query = {'portal_type': 'opengever.repository.repositoryfolder'}
        msg = 'Migrate repositoryfolder title'
        for repository in self.objects(query, msg, savepoints=500):
            self.migrate_repositoryfolder_titles(repository)

    def migrate_repositoryfolder_titles(self, repositoryfolder):
        """Because the repositoryfolder is required, we set the current title
        for both languages.
        """
        ITranslatedTitle(repositoryfolder).title_de = repositoryfolder.effective_title
        ITranslatedTitle(repositoryfolder).title_fr = repositoryfolder.effective_title
        repositoryfolder.reindexObject()
