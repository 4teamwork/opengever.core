from ftw.upgrade import UpgradeStep
from opengever.repository.repositoryroot import RepositoryRoot
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class ChangeRepositoryRootClass(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.repository.upgrades:4501')
        self.migrate_repositoryroot_class()

    def migrate_repositoryroot_class(self):
        query = {'portal_type': 'opengever.repository.repositoryroot'}
        msg = 'Migrate repositoryroot class'
        for repositoryroot in self.objects(query, msg, savepoints=500):
            self.migrate_object(repositoryroot)

    def migrate_object(self, obj):
        self.migrate_class(obj, RepositoryRoot)
        notify(ObjectModifiedEvent(obj))
