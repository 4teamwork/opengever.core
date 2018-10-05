from ftw.upgrade import UpgradeStep
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.mail.mail import IOGMailMarker
from opengever.mail.mail import IOGMail
from ftw.bumblebee.interfaces import IBumblebeeDocument


class UpdateOGMailBumblebeeDocumentChecksums(UpgradeStep):
    """Update og mail bumblebee document checksums.
    """

    deferrable = True

    def __call__(self):
        self.update_bumblebee_mail_checksums()

    def update_bumblebee_mail_checksums(self):
        if not is_bumblebee_feature_enabled():
            return
        for obj in self.objects(
                {'object_provides': IOGMailMarker.__identifier__},
                'Recalculate checksum and rebuild visual preview for mails'):
            if IOGMail(obj).original_message:
                continue
            IBumblebeeDocument(obj).handle_modified()
