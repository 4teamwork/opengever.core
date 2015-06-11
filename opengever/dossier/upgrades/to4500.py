from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.base.behaviors.translated_title import ITranslatedTitle
from plone import api


class ActivateTranslatedTitle(UpgradeStep):
    """Add ITranslatedTitle behavior to Templatedossier
    and migrate titles to title_de.
    """

    def __call__(self):
        self.setup_install_profile('profile-opengever.dossier.upgrades:4500')

        query = {'portal_type': 'opengever.dossier.templatedossier'}
        msg = 'Migrate title of templatedossiers'
        for templatedossier in self.objects(query, msg, savepoints=500):
            self.migrate_titles(templatedossier)

        fti = api.portal.get_tool('portal_types').get(
            'opengever.dossier.templatedossier')
        fti.behaviors = filter(
            lambda b: b != IOpenGeverBase.__identifier__, fti.behaviors)

    def migrate_titles(self, obj):
        ITranslatedTitle(obj).title_de = IOpenGeverBase(obj).title
        obj.reindexObject()
