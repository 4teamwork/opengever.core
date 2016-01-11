from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.base.behaviors.translated_title import ITranslatedTitle
from plone import api


class ActivateTranslatedTitle(UpgradeStep):
    """Add ITranslatedTitle behavior to Inbox and InboxContainer
    and migrate titles to title_de.
    """

    portal_types = ['opengever.inbox.inbox', 'opengever.inbox.container']

    def __call__(self):
        self.setup_install_profile('profile-opengever.inbox.upgrades:4600')

        query = {'portal_type': self.portal_types}
        msg = 'Migrate title of inboxes and inboxcontainers'
        for inbox in self.objects(query, msg):
            self.migrate_titles(inbox)

        self.remove_base_behavior()

    def migrate_titles(self, obj):
        ITranslatedTitle(obj).title_de = IOpenGeverBase(obj).title
        obj.reindexObject()

    def remove_base_behavior(self):
        behavior = IOpenGeverBase.__identifier__
        types_tool = api.portal.get_tool('portal_types')
        for portal_type in self.portal_types:
            fti = types_tool.get(portal_type)
            fti.behaviors = filter(lambda b: b != behavior, fti.behaviors)
