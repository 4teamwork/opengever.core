from ftw.upgrade import UpgradeStep
from opengever.mail.mail import initialize_metadata


class ActivateBehaviors(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-opengever.mail.upgrades:2200')

        query = {'portal_type': 'ftw.mail.mail'}
        for mail in self.objects(query, 'Initialize metadata on mail'):
            initialize_metadata(mail, None)
