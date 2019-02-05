from ftw.upgrade import UpgradeStep
from ftw.upgrade.workflow import WorkflowChainUpdater
from opengever.inbox.container import IInboxContainer
from opengever.inbox.inbox import IInbox
from operator import methodcaller
from plone import api


class AddMailPlacefulWorfklowForInboxArea(UpgradeStep):
    """Add mail placeful worfklow for inbox area.
    """

    def __call__(self):
        inbox_brains = self.catalog_unrestricted_search(
            {'context': api.portal.get(),
             'depth': 1,
             'object_provides': [IInbox.__identifier__, IInboxContainer.__identifier__]},
            full_objects=False)

        inbox_paths = map(methodcaller('getPath'), inbox_brains)
        mails_in_inboxes = self.catalog_unrestricted_search(
            {'path': inbox_paths, 'portal_type': 'ftw.mail.mail'},
            full_objects=True)

        review_state_mapping = {
                    ('opengever_mail_workflow',
                     'opengever_inbox_mail_workflow'): {
                         'mail-state-active': 'mail-state-active',
                         'mail-state-removed': 'mail-state-removed'}
                    }

        with WorkflowChainUpdater(mails_in_inboxes, review_state_mapping):
            self.install_upgrade_profile()
