from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.base.behaviors.translated_title import ITranslatedTitle
from plone import api


class ActivateTranslatedTitle(UpgradeStep):
    """Add ITranslatedTitle behavior to Inbox and InboxContainer
    and migrate titles to title_de.
    """

    def __call__(self):
        self.setup_install_profile('profile-opengever.inbox.upgrades:4500')

        query = {'portal_type': ['opengever.inbox.inbox',
                                 'opengever.inbox.container']}
        msg = 'Migrate title of inboxes and inboxcontainers'
        for inbox in self.objects(query, msg, savepoints=500):
            self.migrate_titles(inbox)

        self.remove_behavior('opengever.inbox.container',
                             IOpenGeverBase.__identifier__)
        self.remove_behavior('opengever.inbox.inbox',
                             IOpenGeverBase.__identifier__)

    def migrate_titles(self, obj):
        ITranslatedTitle(obj).title_de = IOpenGeverBase(obj).title
        obj.reindexObject()

    def remove_behavior(self, portal_type, behavior):
        fti = api.portal.get_tool('portal_types').get(portal_type)
        fti.behaviors = filter(lambda b: b != behavior, fti.behaviors)
