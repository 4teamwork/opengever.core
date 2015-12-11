from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.translated_title import ITranslatedTitle
from plone import api
from plone.app.dexterity.behaviors.metadata import IBasic


class ActivateTranslatedTitle(UpgradeStep):
    """Add ITranslatedTitle behavior to contactfolder and migrate titles
    to title_de.
    """

    portal_types = ['opengever.contact.contactfolder']

    def __call__(self):
        self.setup_install_profile('profile-opengever.contact.upgrades:4600')

        query = {'portal_type': self.portal_types}
        msg = 'Migrate title of contactfolders'
        for contactfolder in self.objects(query, msg, savepoints=500):
            self.migrate_titles(contactfolder)

        self.remove_base_behavior()

    def migrate_titles(self, obj):
        ITranslatedTitle(obj).title_de = IBasic(obj).title
        obj.reindexObject()

    def remove_base_behavior(self):
        behavior = IBasic.__identifier__
        types_tool = api.portal.get_tool('portal_types')
        for portal_type in self.portal_types:
            fti = types_tool.get(portal_type)
            fti.behaviors = filter(lambda b: b != behavior, fti.behaviors)
