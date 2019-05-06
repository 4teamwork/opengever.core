from ftw.mail.mail import IMail
from ftw.upgrade import UpgradeStep


class ReindexFileExtensionForMails(UpgradeStep):
    """Reindex file_extension for mails.
    """

    deferrable = True

    def __call__(self):
        query = {'object_provides': IMail.__identifier__}
        for obj in self.objects(query, 'Reindex file extension'):
            obj.reindexObject(idxs=['file_extension'])
