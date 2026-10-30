from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.ogds.models.user_settings import UserSettings
from opengever.testing import IntegrationTestCase
import json


class TestUsersSettingsGet(IntegrationTestCase):

    @browsing
    def test_returns_default_settings_for_users_without_personal_settings(self, browser):
        self.login(self.regular_user, browser)
        browser.open('{}/@user-settings'.format(self.portal.absolute_url()),
                     headers=self.api_headers)

        self.assertEquals(
            {"notify_inbox_actions": True,
             "seen_tours": ['*'],
             "notify_own_actions": False},
            browser.json)

    @browsing
    def test_returns_personal_settings(self, browser):
        self.login(self.service_user, browser)
        setting = UserSettings(
            userid=self.service_user.id,
            notify_own_actions=True,
            notify_inbox_actions=True,
            _seen_tours=json.dumps(
                ['gever.introduction', 'gever.release-2019.3']))
        create_session().add(setting)

        browser.open('{}/@user-settings'.format(self.portal.absolute_url()),
                     headers=self.api_headers)

        self.assertEquals(
            {u'notify_inbox_actions': True,
             u'seen_tours': [u'gever.introduction', u'gever.release-2019.3'],
             u'notify_own_actions': True},
            browser.json)

    @browsing
    def test_a_pure_plone_user_has_always_seen_all_tours(self, browser):
        # Ogds-user user has not seen tours by default
        self.login(self.service_user, browser)
        self.assertIsNotNone(self.get_ogds_user(self.regular_user))
        browser.open('{}/@user-settings'.format(self.portal.absolute_url()),
                     headers=self.api_headers)
        self.assertEquals([], browser.json.get('seen_tours'))

        # Pure plone user has all tours seen by default
        self.login(self.manager, browser)
        self.assertIsNone(self.get_ogds_user(self.manager))

        browser.open('{}/@user-settings'.format(self.portal.absolute_url()),
                     headers=self.api_headers)
        self.assertEquals([u'*'], browser.json.get('seen_tours'))


class TestUsersSettingsPatch(IntegrationTestCase):

    @browsing
    def test_creates_settings_if_not_exists(self, browser):
        self.login(self.service_user, browser)

        self.assertEquals(
            0, UserSettings.query.filter_by(userid=self.service_user.id).count())

        data = json.dumps(
            {'seen_tours': ['gever.introduction', 'gever.release_2019.3']})
        browser.open('{}/@user-settings'.format(self.portal.absolute_url()),
                     data=data, method='PATCH', headers=self.api_headers)

        self.assertEquals(204, browser.status_code)

        setting = UserSettings.query.filter_by(userid=self.service_user.id).one()
        self.assertEquals(
            json.dumps(['gever.introduction', 'gever.release_2019.3']),
            setting._seen_tours)

    @browsing
    def test_respects_prefer_header(self, browser):
        self.login(self.regular_user, browser)

        headers = self.api_headers.copy()
        headers.update({'Prefer': 'return=representation'})

        data = json.dumps(
            {'seen_tours': ['gever.introduction', 'gever.release-2019.3']})
        browser.open('{}/@user-settings'.format(self.portal.absolute_url()),
                     data=data, method='PATCH', headers=headers)

        self.assertEquals(200, browser.status_code)
        self.assertEquals(
            {"notify_inbox_actions": True,
             "seen_tours": ['gever.introduction', 'gever.release-2019.3'],
             "notify_own_actions": False},
            browser.json)

    @browsing
    def test_values_are_validated(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(400):
            data = json.dumps(
                {'notify_inbox_actions': 'a string',
                 'seen_tours': 235})

            browser.open('{}/@user-settings'.format(self.portal.absolute_url()),
                         data=data, method='PATCH', headers=self.api_headers)

        self.assertEqual(
            {u'message': u"[('notify_inbox_actions', WrongType(u'a string', <type 'bool'>, 'notify_inbox_actions')), ('seen_tours', WrongType(235, <type 'list'>, 'seen_tours'))]",
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_invalid_keys_raises(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(400):
            data = json.dumps(
                {'invalid_key': 'special value',
                 'seen_tours': ['gever.introduction', 'gever.release_2019.3']})

            browser.open('{}/@user-settings'.format(self.portal.absolute_url()),
                         data=data, method='PATCH', headers=self.api_headers)

        self.assertEqual(
            {u'message': "[(u'invalid_key', UnknownField(u'invalid_key'))]",
             u'type': u'BadRequest'},
            browser.json)


class TestNotificationEmailSettings(IntegrationTestCase):

    def enable(self):
        from opengever.base.interfaces import IOGMailSettings
        from plone import api
        api.portal.set_registry_record(
            'alternative_notification_email_enabled', True, IOGMailSettings)

    @browsing
    def test_set_change_and_clear(self, browser):
        self.enable()
        self.login(self.regular_user, browser)
        headers = dict(self.api_headers, Prefer='return=representation')
        for value in [u'private@example.org', u'business@example.org', u'', None]:
            browser.open(self.portal, view='@user-settings', method='PATCH',
                         headers=headers,
                         data=json.dumps({'notification_email': value}))
            self.assertEqual(200, browser.status_code)
            self.assertEqual(value or None, browser.json['notification_email'])
            setting = UserSettings.query.get(self.regular_user.id)
            self.assertEqual(value or None, setting.notification_email)
            self.assertTrue(setting.notify_inbox_actions)

    @browsing
    def test_disabled_field_is_hidden_and_writes_fail_atomically(self, browser):
        self.login(self.regular_user, browser)
        setting = UserSettings.get_or_create(self.regular_user.id)
        setting.notification_email = u'private@example.org'
        browser.open(self.portal, view='@user-settings', headers=self.api_headers)
        self.assertNotIn('notification_email', browser.json)
        for value in [u'new@example.org', u'', None]:
            with browser.expect_http_error(400):
                browser.open(self.portal, view='@user-settings', method='PATCH',
                             headers=self.api_headers, data=json.dumps({
                                 'notification_email': value,
                                 'notify_inbox_actions': False}))
            self.assertTrue(setting.notify_inbox_actions)
            self.assertEqual(u'private@example.org', setting.notification_email)

    @browsing
    def test_invalid_updates_are_atomic(self, browser):
        self.enable()
        self.login(self.regular_user, browser)
        setting = UserSettings.get_or_create(self.regular_user.id)
        setting.notification_email = u'private@example.org'
        for value in [u'invalid', 42, [], {}, u'x' * 256 + u'@example.org']:
            with browser.expect_http_error(400):
                browser.open(self.portal, view='@user-settings', method='PATCH',
                             headers=self.api_headers, data=json.dumps({
                                 'notification_email': value,
                                 'notify_inbox_actions': False}))
            self.assertEqual(u'private@example.org', setting.notification_email)
            self.assertTrue(setting.notify_inbox_actions)

    @browsing
    def test_only_current_user_can_access_setting(self, browser):
        self.enable()
        self.login(self.regular_user, browser)
        setting = UserSettings.get_or_create(self.regular_user.id)
        setting.notification_email = u'private@example.org'
        for other in [self.dossier_responsible, self.administrator]:
            self.login(other, browser)
            browser.open(self.portal, view='@user-settings', headers=self.api_headers)
            self.assertIsNone(browser.json['notification_email'])
            with browser.expect_http_error(400):
                browser.open(self.portal, view='@user-settings', method='PATCH',
                             headers=self.api_headers, data=json.dumps({
                                 'userid': self.regular_user.id,
                                 'notification_email': u'stolen@example.org'}))
            self.assertEqual(u'private@example.org', setting.notification_email)
            for view in ['@ogds-users/' + self.regular_user.id, '@ogds-user-listing',
                         '@users/' + self.regular_user.id]:
                browser.open(self.portal, view=view, headers=self.api_headers)
                self.assertNotIn('private@example.org', json.dumps(browser.json))
                self.assertNotIn('notification_email', json.dumps(browser.json))

    @browsing
    def test_channel_endpoints_cannot_write_or_reset_notification_email(self, browser):
        self.login(self.regular_user, browser)
        setting = UserSettings.get_or_create(self.regular_user.id)
        setting.notification_email = u'private@example.org'
        for enabled in [False, True]:
            if enabled:
                self.enable()
            for payload in [{'value': True}, {'reset': True}]:
                with browser.expect_http_error(400):
                    browser.open(self.portal,
                                 view='@notification-settings/general/notification_email',
                                 method='PATCH', headers=self.api_headers,
                                 data=json.dumps(payload))
            for method in ['save_user_setting', 'reset_user_setting']:
                with browser.expect_http_error(400):
                    browser.open(self.portal, view='notification-settings/' + method,
                                 data={'config_name': 'notification_email',
                                       'value': json.dumps('invalid')})
            self.assertEqual(u'private@example.org', setting.notification_email)

    def test_document_properties_exclude_notification_email(self):
        from opengever.dossier.docprops import DefaultMemberDocPropertyProvider
        self.login(self.regular_user)
        setting = UserSettings.get_or_create(self.regular_user.id)
        setting.notification_email = u'private@example.org'
        provider = DefaultMemberDocPropertyProvider(self.regular_user)
        self.assertNotIn('notification_email', provider.ogds_user_attributes)
        self.assertNotIn('private@example.org', repr(provider.get_properties()))
