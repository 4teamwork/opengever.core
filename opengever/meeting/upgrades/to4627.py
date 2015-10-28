from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.base.behaviors.translated_title import ITranslatedTitle
from plone import api


class ActivateTranslatedTitle(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-opengever.meeting.upgrades:4627')

        query = {'portal_type': 'opengever.meeting.committeecontainer'}
        msg = 'Migrate committeecontainer titles'
        for container in self.objects(query, msg, savepoints=500):
            self.migrate_titles(container)

        self.remove_base_behaviors()

    def migrate_titles(self, obj):
        ITranslatedTitle(obj).title_de = IOpenGeverBase(obj).title
        obj.reindexObject()

    def remove_base_behaviors(self):
        fti = api.portal.get_tool('portal_types').get(
            'opengever.meeting.committeecontainer')
        fti.behaviors = filter(
            lambda b: b != IOpenGeverBase.__identifier__, fti.behaviors)
