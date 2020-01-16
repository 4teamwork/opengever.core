from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.translated_title import ITranslatedTitle


class UpdateRepositoryRootFrenchTitle(UpgradeStep):
    """Update repository root french title.
    """

    def __call__(self):
        self.install_upgrade_profile()
        query = {'portal_type': ['opengever.repository.repositoryroot']}
        for root in self.objects(query, 'Set french title on repository root'):
            if not ITranslatedTitle(root).title_fr:
                ITranslatedTitle(root).title_fr = u'Syst\xe8me de classement'
                root.reindexObject(idxs=['title_fr'])
