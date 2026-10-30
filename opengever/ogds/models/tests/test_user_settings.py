from opengever.ogds.models.tests.base import OGDSTestCase
from opengever.ogds.models.user_settings import UserSettings


class TestNotificationEmailSetting(OGDSTestCase):

    def test_missing_row_defaults(self):
        self.assertIsNone(UserSettings.get_setting(None, 'notification_email'))
        self.assertFalse(UserSettings.get_setting(None, 'notify_own_actions'))
        self.assertEqual([], UserSettings.get_setting(None, 'seen_tours'))

    def test_survives_identity_updates_and_deactivation(self):
        settings = UserSettings(userid=self.john.userid,
                                notification_email=u'private@example.org')
        self.session.add(settings)
        self.session.flush()
        self.john.email = 'new-account@example.org'
        self.john.active = False
        self.session.flush()
        self.session.expire_all()
        self.assertEqual(u'private@example.org',
                         self.john.user_settings.notification_email)
