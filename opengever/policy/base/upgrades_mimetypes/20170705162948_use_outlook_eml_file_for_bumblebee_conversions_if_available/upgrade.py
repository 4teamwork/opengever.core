from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.upgrade import UpgradeStep
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.mail.mail import IOGMail
from opengever.mail.mail import IOGMailMarker


class UseOutlookEMLFileForBumblebeeConversionsIfAvailable(UpgradeStep):
    """Use outlook eml file for bumblebee conversions if available.
    """

    def __call__(self):
        self.install_upgrade_profile()

        if not is_bumblebee_feature_enabled():
            return

        for obj in self.objects(
                {'object_provides': IOGMailMarker.__identifier__},
                'Reset contenttype and rebuild visual preview for mails'):

            original_message = IOGMail(obj).original_message
            if not original_message:
                continue

            original_message.contentType = 'application/vnd.ms-outlook'
            IBumblebeeDocument(obj).handle_modified()
