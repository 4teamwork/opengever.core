from ftw.mail.interfaces import IMailSettings as IFtwMailSettings
from ftw.upgrade import UpgradeStep
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class MigrateMailDomainRegistrySetting(UpgradeStep):

    def __call__(self):
        # Make sure the IMailSettings registry settings interface for
        # ftw.mail have already been registered
        self.setup_install_profile('profile-ftw.mail.upgrades:2000')

        registry = getUtility(IRegistry)
        OG_MAIL_SETTINGS_KEY = 'opengever.mail.interfaces.IMailSettings.mail_domain'

        try:
            mail_domain = registry[OG_MAIL_SETTINGS_KEY]
        except KeyError:
            # og.mail settings have already been removed
            pass
        else:
            # No exception, migrate settings and remove old records
            ftw_mail_settings = registry.forInterface(IFtwMailSettings)
            ftw_mail_settings.mail_domain = mail_domain

            # Unregister the old opengever.mail settings
            del registry.records[OG_MAIL_SETTINGS_KEY]
