from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.translated_title import ITranslatedTitle
from plone import api
from plone.app.dexterity.behaviors.metadata import IBasic


class ActivateTranslatedTitle(UpgradeStep):

    def __call__(self):

        self.setup_install_profile(
            'profile-opengever.repository.upgrades:4500')

        query = {'portal_type': 'opengever.repository.repositoryfolder'}
        msg = 'Migrate repositoryfolder title'
        for repository in self.objects(query, msg, savepoints=500):
            self.migrate_repository_folder_title(repository)

        query = {'portal_type': 'opengever.repository.repositoryroot'}
        msg = 'Migrate repositoryroot title'
        for repository in self.objects(query, msg, savepoints=500):
            self.migrate_repositoryroot_titles(repository)

        self.remove_basic_behavior()

    def migrate_repositoryroot_titles(self, repositoryroot):
        ITranslatedTitle(repositoryroot).title_de = IBasic(repositoryroot).title
        repositoryroot.reindexObject()

    def migrate_repository_folder_title(self, repository):
        ITranslatedTitle(repository).title_de = repository.effective_title
        repository.reindexObject()

    def remove_basic_behavior(self):
        fti = api.portal.get_tool('portal_types').get(
            'opengever.repository.repositoryroot')
        fti.behaviors = filter(lambda b:
                               b != IBasic.__identifier__, fti.behaviors)
