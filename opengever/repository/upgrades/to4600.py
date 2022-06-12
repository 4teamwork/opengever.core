from ftw.upgrade import UpgradeStep
from opengever.repository.repositoryroot import RepositoryRoot


class MigrateRepositoryRootClass(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.repository.upgrades:4600')

        for obj in self.objects(
            {'portal_type': 'opengever.repository.repositoryroot'},
            'Migrate Repositoryroot class'
        ):
            self.migrate_class(obj, RepositoryRoot)
