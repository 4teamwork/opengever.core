from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from plone import api


class ModifyTitleFrOfPrivateRepositoryRoot(UpgradeStep):
    """Modify title fr of private repository root.
    """

    def __call__(self):
        mtool = api.portal.get_tool('portal_membership')
        private_root = mtool.getMembersFolder()

        if ITranslatedTitleSupport.providedBy(private_root):
            ITranslatedTitle(private_root).title_fr = u"Dossier personnel"
