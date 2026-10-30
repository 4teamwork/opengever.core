from opengever.activity.notification_email import get_notification_email
from opengever.base.interfaces import IOGMailSettings
from opengever.ogds.models.user_settings import UserSettings
from opengever.testing import IntegrationTestCase
from plone import api


class TestNotificationEmail(IntegrationTestCase):

    def test_flag_and_fallback_matrix(self):
        self.login(self.regular_user)
        user = self.get_ogds_user(self.regular_user)
        self.assertIsNone(get_notification_email(None))
        self.assertEqual(user.email, get_notification_email(user))
        setting = UserSettings.get_or_create(user.userid)
        setting.notification_email = u'private@example.org'
        self.assertEqual(user.email, get_notification_email(user))
        api.portal.set_registry_record(
            'alternative_notification_email_enabled', True, IOGMailSettings)
        self.assertEqual(u'private@example.org', get_notification_email(user))
        user.email = None
        self.assertEqual(u'private@example.org', get_notification_email(user))
        setting.notification_email = None
        self.assertIsNone(get_notification_email(user))
        user.email = u'primary@example.org'
        self.assertEqual(user.email, get_notification_email(user))
