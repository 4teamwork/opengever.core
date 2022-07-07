from ftw.upgrade import UpgradeStep
from opengever.workspace import is_workspace_feature_enabled
from plone import api


class EnableAllLanguagesForTeamraum(UpgradeStep):
    """Enable all languages for teamraum.
    """
    language_mapping = {
        'de': 'de-ch',
        'fr': 'fr-ch',
        'en': 'en-us',
    }

    def __call__(self):
        if is_workspace_feature_enabled():
            return

        lang_tool = api.portal.get_tool('portal_languages')

        # Before installing the new profile we remember the current default
        # language to set it back after.
        default = lang_tool.getDefaultLanguage()
        default = self.language_mapping.get(default, default)
        self.install_upgrade_profile()
        if default:
            lang_tool.setDefaultLanguage(default)

        self.set_titles()

    def set_titles(self):
        catalog = api.portal.get_tool('portal_catalog')
        for brain in catalog.unrestrictedSearchResults(portal_type="opengever.workspace.root"):
            obj = brain.getObject()
            obj.title_en = u"Workspaces"
            obj.title_fr = u"Espaces de travail"
            obj.reindexObject(idxs=["UID", "title_en", "title_fr"])
