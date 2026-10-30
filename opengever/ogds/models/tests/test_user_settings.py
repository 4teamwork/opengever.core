from opengever.ogds.models.tests.base import OGDSTestCase
from opengever.ogds.models.user_settings import IUserSettings
from opengever.ogds.models.user_settings import UserSettings
from zope.schema import ValidationError


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

    def test_mailbox_and_domain_label_length_boundaries(self):
        field = IUserSettings['notification_email']
        field.validate(u'a' * 64 + u'@example.org')
        field.validate(u'a@' + u'b' * 63 + u'.org')
        for value in [u'a' * 65 + u'@example.org', u'a@' + u'b' * 64 + u'.org',
                      u'a@example.' + u'b' * 64]:
            with self.assertRaises(ValidationError):
                field.validate(value)

    def test_schema_rejects_invalid_addresses_types_and_length(self):

        field = IUserSettings['notification_email']
        for value in [u'not-an-email', u'a@example.org,b@example.org',
                      u'Name <a@example.org>', u'a@example.org\nBcc: b@example.org',
                      u'a..b@example.org', u'@example.org',
                      u'a' * 250 + u'@example.org', 123, [], {}]:
            with self.assertRaises(ValidationError):
                field.validate(value)
        for value in [None, u'private+notifications@example.org']:
            field.validate(value)
