from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.base.behaviors.translated_title import ITranslatedTitle
from plone import api


class ActivateTranslatedTitle(UpgradeStep):
    """Add ITranslatedTitle behavior to Templatedossier and migrate titles to
    title_de. It removes the IOpenGeverBase behavior as well.
    """

    def __call__(self):
        self.setup_install_profile('profile-opengever.dossier.upgrades:4600')

        query = {'portal_type': 'opengever.dossier.templatedossier'}
        msg = 'Migrate title of templatedossiers'
        for templatedossier in self.objects(query, msg):
            self.migrate_titles(templatedossier)

        self.remove_base_behavior()

    def migrate_titles(self, obj):
        ITranslatedTitle(obj).title_de = IOpenGeverBase(obj).title
        obj.reindexObject()

    def remove_base_behavior(self):
        fti = api.portal.get_tool('portal_types').get(
            'opengever.dossier.templatedossier')
        fti.behaviors = filter(
            lambda b: b != IOpenGeverBase.__identifier__, fti.behaviors)
