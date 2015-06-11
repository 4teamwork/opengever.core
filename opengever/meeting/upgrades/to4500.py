from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.base.behaviors.translated_title import ITranslatedTitle
from plone import api


class ActivateTranslatedTitle(UpgradeStep):

    def __call__(self):

        self.setup_install_profile(
            'profile-opengever.meeting.upgrades:4500')

        query = {'portal_type': 'opengever.meeting.committeecontainer'}
        msg = 'Migrate committeecontainer titles'
        for repository in self.objects(query, msg, savepoints=500):
            self.migrate_titles(repository)

        fti = api.portal.get_tool('portal_types').get(
            'opengever.meeting.committeecontainer')
        fti.behaviors = filter(
            lambda b: b != IOpenGeverBase.__identifier__, fti.behaviors)

    def migrate_titles(self, obj):
        ITranslatedTitle(obj).title_de = obj.title
        obj.reindexObject()
