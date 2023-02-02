from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyMailAttachmentInfoUpdater


class UpdateMailAttachmentInfos(UpgradeStep):
    """Update mail attachment infos.
    """

    deferrable = True

    def __call__(self):
        query = {'portal_type': 'ftw.mail.mail'}
        with NightlyMailAttachmentInfoUpdater() as attachment_updater:
            for brain in self.brains(query, 'Queueing update attachment info jobs'):
                attachment_updater.add_by_brain(brain)
