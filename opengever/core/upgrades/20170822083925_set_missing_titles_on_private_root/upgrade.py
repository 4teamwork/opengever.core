from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.translated_title import ITranslatedTitle


class SetMissingTitlesOnPrivateRoot(UpgradeStep):
    """Set missing titles on private root.
    """

    def __call__(self):
        query = {'portal_type': ['opengever.private.root']}
        for folder in self.objects(query, 'Set title on private root folders'):
            idxs = []

            if not ITranslatedTitle(folder).title_de:
                ITranslatedTitle(folder).title_de = u'Meine Ablage'
                idxs.append('title_de')
            if not ITranslatedTitle(folder).title_fr:
                ITranslatedTitle(folder).title_fr = u'Mon depot'
                idxs.append('title_fr')

            if idxs:
                folder.reindexObject(idxs=idxs)
