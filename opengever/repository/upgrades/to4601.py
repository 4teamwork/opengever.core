from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.translated_title import ITranslatedTitle
from plone import api
from plone.app.dexterity.behaviors.metadata import IBasic


class TranslatedTitleForRepositoryRoots(UpgradeStep):

    portal_type = 'opengever.repository.repositoryroot'

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.repository.upgrades:4601')

        query = {'portal_type': 'opengever.repository.repositoryroot'}
        msg = 'Migrate repositoryroot title'
        for repository in self.objects(query, msg):
            self.migrate_repositoryroot_titles(repository)

        self.remove_basic_behavior()

    def migrate_repositoryroot_titles(self, repositoryroot):
        ITranslatedTitle(repositoryroot).title_de = IBasic(repositoryroot).title
        repositoryroot.reindexObject()

    def remove_basic_behavior(self):
        fti = api.portal.get_tool('portal_types').get(self.portal_type)
        fti.behaviors = filter(lambda b:
                               b != IBasic.__identifier__, fti.behaviors)
