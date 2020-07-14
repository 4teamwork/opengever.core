from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.translated_title import ITranslatedTitle


class UpdateITranslatedTitleOfPrivateRoot(UpgradeStep):
    """Update ITranslatedTitle of private root.
    """

    def __call__(self):

        query = {'portal_type': ['opengever.private.root']}
        for obj in self.objects(query, 'Rename private root.'):
            ITranslatedTitle(obj).title_fr = u'Mon d\xe9p\xf4t'
            obj.reindexObject(idxs=['title_fr'])
