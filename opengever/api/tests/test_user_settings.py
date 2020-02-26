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
             "seen_tours": [],
             "notify_own_actions": False},
            browser.json)

    @browsing
    def test_returns_personal_settings(self, browser):
        self.login(self.regular_user, browser)
        setting = UserSettings(
            userid=self.regular_user.id,
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
        # Ogds-user user has no seen tours by default
        self.login(self.regular_user, browser)
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
        self.login(self.regular_user, browser)

        self.assertEquals(
            0, UserSettings.query.filter_by(userid=self.regular_user.id).count())

        data = json.dumps(
            {'seen_tours': ['gever.introduction', 'gever.release_2019.3']})
        browser.open('{}/@user-settings'.format(self.portal.absolute_url()),
                     data=data, method='PATCH', headers=self.api_headers)

        self.assertEquals(204, browser.status_code)

        setting = UserSettings.query.filter_by(userid=self.regular_user.id).one()
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
