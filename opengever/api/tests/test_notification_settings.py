from ftw.testbrowser import browsing
from opengever.activity import model
from opengever.activity.notification_settings import NotificationSettings
from opengever.ogds.models.user_settings import UserSettings
from opengever.testing import IntegrationTestCase
import json


class TestNotificationSettings(IntegrationTestCase):

    features = ('activity', )

    def test_get_configuration_by_id_returns_the_configuration(self):
        setting1 = {'id': 'setting-1'}
        setting2 = {'id': 'setting-2'}
        settings = NotificationSettings([setting1, setting2])

        self.assertIs(setting2, settings.get_configuration_by_id('setting-2'))

    def test_get_configuration_by_id_returns_default_value_if_not_found(self):
        settings = NotificationSettings([])

        self.assertIsNone(settings.get_configuration_by_id('setting-1'))
        self.assertEqual({}, settings.get_configuration_by_id('setting-1', {}))

    def test_get_configuration_by_activity_kind(self):
        setting1 = {'id': 'setting-1', 'activities': ['activity-1', 'activity-2']}
        setting2 = {'id': 'setting-2', 'activities': ['activity-3']}
        settings = NotificationSettings([setting1, setting2])

        self.assertIs(setting1, settings.get_configuration_by_activity_kind('activity-1'))
        self.assertIs(setting1, settings.get_configuration_by_activity_kind('activity-2'))
        self.assertIs(setting2, settings.get_configuration_by_activity_kind('activity-3'))

    def test_get_configuration_by_activity_kind_returns_default_value_if_not_found(self):
        setting1 = {'id': 'setting-1', 'activities': ['activity-1']}
        settings = NotificationSettings([setting1])

        self.assertIsNone(settings.get_configuration_by_activity_kind('activity-2'))
        self.assertEqual({}, settings.get_configuration_by_activity_kind('activity-2', {}))

    def test_get_settings_returns_the_settings_for_the_user(self):
        settings = NotificationSettings().get_settings(self.regular_user.getId())
        self.assertEqual(
            frozenset([u'regular_watcher', u'task_issuer', u'task_responsible']),
            settings.get('task-added-or-reassigned').badge_notification_roles)

    def test_get_settings_respects_custom_user_settings(self):
        userid = self.regular_user.getId()
        notification_settings = NotificationSettings()

        settings = notification_settings.get_settings(userid)
        self.assertIsInstance(settings.get('task-added-or-reassigned'), model.NotificationDefault)
        self.assertEqual(
            frozenset([u'regular_watcher', u'task_issuer', u'task_responsible']),
            settings.get('task-added-or-reassigned').badge_notification_roles)

        notification_settings.set_custom_setting(
            'task-added-or-reassigned', userid,
            badge_roles=[u'task_responsible'])

        settings = notification_settings.get_settings(userid)
        self.assertIsInstance(settings.get('task-added-or-reassigned'), model.NotificationSetting)
        self.assertEqual(
            frozenset([u'task_responsible']),
            settings.get('task-added-or-reassigned').badge_notification_roles)

    def test_get_settings_merges_default_and_custom_settings(self):
        userid = self.regular_user.getId()
        notification_settings = NotificationSettings()

        settings = notification_settings.get_settings(userid)
        self.assertIsInstance(settings.get('task-added-or-reassigned'), model.NotificationDefault)
        self.assertIsInstance(settings.get('task-reminder'), model.NotificationDefault)

        notification_settings.set_custom_setting(
            'task-added-or-reassigned', userid,
            badge_roles=[u'task_responsible'])

        settings = notification_settings.get_settings(userid)
        self.assertIsInstance(settings.get('task-added-or-reassigned'), model.NotificationSetting)
        self.assertIsInstance(settings.get('task-reminder'), model.NotificationDefault)

    def test_get_setting_returns_a_specific_notification_setting(self):
        setting = NotificationSettings().get_setting('task-added-or-reassigned', self.regular_user.getId())
        self.assertEqual(
            frozenset([u'regular_watcher', u'task_issuer', u'task_responsible']),
            setting.badge_notification_roles)

    def test_get_setting_respects_custom_user_settings(self):
        userid = self.regular_user.getId()
        notification_settings = NotificationSettings()

        setting = notification_settings.get_setting('task-added-or-reassigned', userid)
        self.assertIsInstance(setting, model.NotificationDefault)
        self.assertEqual(
            frozenset([u'regular_watcher', u'task_issuer', u'task_responsible']),
            setting.badge_notification_roles)

        notification_settings.set_custom_setting(
            'task-added-or-reassigned', userid,
            badge_roles=[u'task_responsible'])

        setting = notification_settings.get_setting('task-added-or-reassigned', userid)
        self.assertIsInstance(setting, model.NotificationSetting)
        self.assertEqual(
            frozenset([u'task_responsible']),
            setting.badge_notification_roles)

    def test_get_setting_by_activity_kind_returns_a_specific_notification_setting_related_to_an_activity_kind(self):
        setting = NotificationSettings().get_setting_by_activity_kind('task-added', self.regular_user.getId())
        self.assertEqual(
            frozenset([u'regular_watcher', u'task_issuer', u'task_responsible']),
            setting.badge_notification_roles)

    def test_get_setting_by_activity_kind_respects_custom_user_settings(self):
        userid = self.regular_user.getId()
        notification_settings = NotificationSettings()

        setting = notification_settings.get_setting_by_activity_kind('task-added', userid)
        self.assertIsInstance(setting, model.NotificationDefault)
        self.assertEqual(
            frozenset([u'regular_watcher', u'task_issuer', u'task_responsible']),
            setting.badge_notification_roles)

        notification_settings.set_custom_setting(
            'task-added-or-reassigned', userid,
            badge_roles=[u'task_responsible'])

        setting = notification_settings.get_setting_by_activity_kind('task-added', userid)
        self.assertIsInstance(setting, model.NotificationSetting)
        self.assertEqual(
            frozenset([u'task_responsible']),
            setting.badge_notification_roles)

    def test_remove_custom_setting_removes_a_custom_setting(self):
        notification_settings = NotificationSettings()
        userid = self.regular_user.getId()

        setting = notification_settings.get_setting('task-added-or-reassigned', userid)
        self.assertIsInstance(setting, model.NotificationDefault)

        setting = notification_settings.set_custom_setting('task-added-or-reassigned', userid)

        self.assertIsInstance(setting, model.NotificationSetting)

        notification_settings.remove_custom_setting('task-added-or-reassigned', userid)
        setting = notification_settings.get_setting('task-added-or-reassigned', userid)
        self.assertIsInstance(setting, model.NotificationDefault)

    def test_set_custom_setting_adds_a_new_custom_setting_entry(self):
        notification_settings = NotificationSettings()
        userid = self.regular_user.getId()

        setting = notification_settings.get_setting('task-added-or-reassigned', userid)
        self.assertIsInstance(setting, model.NotificationDefault)

        notification_settings.set_custom_setting(
            'task-added-or-reassigned', userid,
            mail_roles=['task_responsible'],
            badge_roles=['regular_watcher'],
            digest_roles=['task_issuer', 'task_responsible'])

        setting = notification_settings.get_setting('task-added-or-reassigned', userid)
        self.assertIsInstance(setting, model.NotificationSetting)

        self.assertEqual(frozenset([u'task_responsible']),
                         setting.mail_notification_roles)

        self.assertEqual(frozenset([u'regular_watcher']),
                         setting.badge_notification_roles)

        self.assertEqual(frozenset([u'task_issuer', u'task_responsible']),
                         setting.digest_notification_roles)

    def test_set_custom_setting_updates_an_existing_custom_setting(self):
        notification_settings = NotificationSettings()
        userid = self.regular_user.getId()

        notification_settings.set_custom_setting(
            'task-added-or-reassigned', userid,
            mail_roles=['task_responsible'],
            badge_roles=['task_issuer'],
            digest_roles=['task_issuer', 'task_responsible'])

        setting = notification_settings.get_setting('task-added-or-reassigned', userid)
        self.assertEqual(frozenset([u'task_responsible']),
                         setting.mail_notification_roles)

        self.assertEqual(frozenset([u'task_issuer']),
                         setting.badge_notification_roles)

        self.assertEqual(frozenset([u'task_issuer', u'task_responsible']),
                         setting.digest_notification_roles)

        notification_settings.set_custom_setting(
            'task-added-or-reassigned', userid, mail_roles=['regular_watcher'], digest_roles=[])

        setting = notification_settings.get_setting('task-added-or-reassigned', userid)
        self.assertEqual(frozenset([u'regular_watcher']),
                         setting.mail_notification_roles)

        self.assertEqual(frozenset([u'task_issuer']),
                         setting.badge_notification_roles)

        self.assertEqual(frozenset([]),
                         setting.digest_notification_roles)

    def test_is_custom_setting_returns_true_if_setting_is_a_custom_setting(self):
        userid = self.regular_user.getId()
        notification_settings = NotificationSettings()

        setting = notification_settings.get_setting('task-added-or-reassigned', userid)
        self.assertFalse(notification_settings.is_custom_setting(setting))

        notification_settings.set_custom_setting(
            'task-added-or-reassigned', userid,
            badge_roles=[u'task_responsible'])

        setting = notification_settings.get_setting('task-added-or-reassigned', userid)
        self.assertTrue(notification_settings.is_custom_setting(setting))


class TestNotificationSettingsGet(IntegrationTestCase):
    features = ('activity', )

    @browsing
    def test_get_notification_settings_for_gever(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='/@notification-settings',
                     method='GET', headers=self.api_headers)

        self.assertEqual({
            u'@id': u'http://nohost/plone/@notification-settings/activities/added-as-watcher',
            u'badge': {u'always': True},
            u'digest': {u'always': False},
            u'group': u'general',
            u'id': u'added-as-watcher',
            u'kind': u'added-as-watcher',
            u'mail': {u'always': False},
            u'personal': False,
            u'title': u'Added as watcher'
        }, browser.json['activities']['items'][0])

        self.assertEqual([
            u'added-as-watcher',
            u'external-activity',
            u'task-added-or-reassigned',
            u'task-transition-modify-deadline',
            u'task-commented',
            u'task-status-modified',
            u'task-reminder',
            u'dossier-overdue',
            u'document-modified',
        ], [activity['kind'] for activity in browser.json['activities']['items']])

        self.assertEqual({
            u'@id': u'http://nohost/plone/@notification-settings/general/notify_inbox_actions',
            u'group': u'general',
            u'help_text': u'Enabled or disable, respectively, all notifications based on your inbox permissions.',
            u'id': u'notify_inbox_actions',
            u'personal': False,
            u'title': u'Enable notifications for inbox activities',
            u'value': True
        }, browser.json['general']['items'][-1])

        self.assertEqual([u'notify_own_actions', u'notify_inbox_actions'],
                         [activity['id'] for activity in browser.json['general']['items']])

        self.assertItemsEqual([
            {u'id': u'always', u'title': u''},
            {u'id': u'dossier_responsible_role', u'title': u'Dossier responsible'},
            {u'id': u'task_reminder_watcher_role', u'title': u'Watcher'},
            {u'id': u'task_issuer', u'title': u'Task issuer'},
            {u'id': u'task_responsible', u'title': u'Task responsible'},
            {u'id': u'regular_watcher', u'title': u'Watcher'}
        ], browser.json['translations'])

    @browsing
    def test_get_notification_settings_for_teamraum(self, browser):
        self.activate_feature('workspace')
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='/@notification-settings',
                     method='GET', headers=self.api_headers)

        self.assertEqual({
            u'@id': u'http://nohost/plone/@notification-settings',
            u'activities': {
                u'@id': u'http://nohost/plone/@notification-settings/activities',
                u'items': [{
                    u'@id': u'http://nohost/plone/@notification-settings/activities/todo-assigned',
                    u'badge': {u'todo_responsible_role': True,
                               u'workspace_member_role': False},
                    u'digest': {u'todo_responsible_role': False,
                                u'workspace_member_role': False},
                    u'group': u'workspace',
                    u'id': u'todo-assigned',
                    u'kind': u'todo-assigned',
                    u'mail': {u'todo_responsible_role': False,
                              u'workspace_member_role': False},
                    u'personal': False,
                    u'title': u'ToDo assigned'},
                    {u'@id': u'http://nohost/plone/@notification-settings/activities/todo-modified',
                     u'badge': {u'todo_responsible_role': True,
                                u'workspace_member_role': False},
                     u'digest': {u'todo_responsible_role': False,
                                 u'workspace_member_role': False},
                     u'group': u'workspace',
                     u'id': u'todo-modified',
                     u'kind': u'todo-modified',
                     u'mail': {u'todo_responsible_role': False,
                               u'workspace_member_role': False},
                     u'personal': False,
                     u'title': u'ToDo modified'},
                    {u'@id': u'http://nohost/plone/@notification-settings/activities/document-modified',
                     u'badge': {u'regular_watcher': True},
                             u'digest': {u'regular_watcher': False},
                             u'group': u'document',
                             u'id': u'document-modified',
                             u'kind': u'document-modified',
                             u'mail': {u'regular_watcher': False},
                             u'personal': False,
                             u'title': u'Document modified'}]},
            u'general': {
                u'@id': u'http://nohost/plone/@notification-settings/general',
                u'items': [{
                    u'@id': u'http://nohost/plone/@notification-settings/general/notify_own_actions',
                    u'group': u'general',
                    u'help_text': u"By default no notifications are emitted for a user's own "
                                  u"actions. This option allows to modify this behavior. "
                                  u"Irrespective of this setting, individual settings for specific "
                                  u"action types will still get applied.",
                    u'id': u'notify_own_actions',
                    u'personal': False,
                    u'title': u'Enable notifications for own actions',
                    u'value': False}]},
            u'translations': [{
                u'id': u'todo_responsible_role',
                u'title': u'ToDo responsible'},
                {u'id': u'regular_watcher', u'title': u'Watcher'},
                {u'id': u'workspace_member_role',
                 u'title': u'Workspace member'}]}, browser.json)


class TestNotificationSettingsPatch(IntegrationTestCase):
    features = ('activity', )

    @browsing
    def test_reset_activity_notification_setting(self, browser):
        self.login(self.regular_user, browser=browser)
        NotificationSettings().set_custom_setting(
            'added-as-watcher', self.regular_user.getId(),
            mail_roles=[u'always'])

        browser.open(self.portal.absolute_url() + '/@notification-settings',
                     method='GET', headers=self.api_headers)

        self.assertEqual({u'always': True}, browser.json['activities']['items'][0]['mail'])
        self.assertEqual(True, browser.json['activities']['items'][0]['personal'])

        browser.open(self.portal.absolute_url() +
                     '/@notification-settings/activities/added-as-watcher', method='PATCH',
                     data=json.dumps({'reset': True}),
                     headers=self.api_headers)

        self.assertEqual(204, browser.status_code)

        browser.open(self.portal.absolute_url() + '/@notification-settings',
                     method='GET', headers=self.api_headers)

        self.assertEqual({u'always': False}, browser.json[
                         'activities']['items'][0]['mail'])
        self.assertEqual(False, browser.json['activities']['items'][0]['personal'])

    @browsing
    def test_reset_general_notification_setting(self, browser):
        self.login(self.regular_user, browser=browser)
        UserSettings.save_setting_for_user(self.regular_user.getId(), 'notify_own_actions', True)

        browser.open(self.portal.absolute_url() + '/@notification-settings',
                     method='GET', headers=self.api_headers)

        self.assertEqual(True, browser.json['general']['items'][0]['value'])
        self.assertEqual(True, browser.json['general']['items'][0]['personal'])

        browser.open(self.portal.absolute_url() +
                     '/@notification-settings/general/notify_own_actions', method='PATCH',
                     data=json.dumps({u'reset': True}),
                     headers=self.api_headers)

        self.assertEqual(204, browser.status_code)

        browser.open(self.portal.absolute_url() + '/@notification-settings',
                     method='GET', headers=self.api_headers)

        self.assertEqual(False, browser.json['general']['items'][0]['value'])
        self.assertEqual(False, browser.json['general']['items'][0]['personal'])

    @browsing
    def test_patch_activity_notification_setting(self, browser):
        self.login(self.regular_user, browser=browser)
        kind = 'task-added-or-reassigned'

        url = '{}/@notification-settings/activities/{}'.format(self.portal.absolute_url(), kind)
        browser.open(url, method='PATCH',
                     data=json.dumps({u'mail': {}, u'digest': {u'task_issuer': True}}),
                     headers=self.api_headers)

        self.assertEqual(204, browser.status_code)

        browser.open(self.portal.absolute_url() + '/@notification-settings',
                     method='GET', headers=self.api_headers)

        result = [item for item in browser.json['activities']['items']
                  if item['kind'] == kind]

        self.assertEqual([{
            u'@id': url,
            u'id': kind,
            u'kind': kind,
            u'badge': {u'regular_watcher': True,
                       u'task_issuer': True,
                       u'task_responsible': True},
            u'digest': {u'regular_watcher': False,
                        u'task_issuer': True,
                        u'task_responsible': False},
            u'mail': {u'regular_watcher': False,
                      u'task_issuer': False,
                      u'task_responsible': False},
            u'personal': True,
            u'group': u'task',
            u'title': u'Task added / reassigned'}], result)

    @browsing
    def test_patch_general_notification_setting(self, browser):
        self.login(self.regular_user, browser=browser)
        setting_id = 'notify_own_actions'

        url = '{}/@notification-settings/general/{}'.format(self.portal.absolute_url(), setting_id)
        browser.open(url, method='PATCH',
                     data=json.dumps({u'value': True}),
                     headers=self.api_headers)

        self.assertEqual(204, browser.status_code)

        browser.open(self.portal.absolute_url() + '/@notification-settings',
                     method='GET', headers=self.api_headers)

        self.assertEqual(True, browser.json['general']['items'][0]['value'])
        self.assertEqual(True, browser.json['general']['items'][0]['personal'])

    @browsing
    def test_patch_invalid_activity_setting_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        kind = 'unknown'

        url = '{}/@notification-settings/activities/{}'.format(self.portal.absolute_url(), kind)
        with browser.expect_http_error(400):
            browser.open(url, method='PATCH',
                         data=json.dumps({u'mail': {}}),
                         headers=self.api_headers)
        self.assertEqual(
            {"message": "'{}' does not exist".format(kind),
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_patch_invalid_general_setting_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        setting_id = 'unknown'

        url = '{}/@notification-settings/general/{}'.format(self.portal.absolute_url(), setting_id)
        with browser.expect_http_error(400):
            browser.open(url, method='PATCH',
                         data=json.dumps({u'value': True}),
                         headers=self.api_headers)
        self.assertEqual(
            {"message": "'{}' does not exist".format(setting_id),
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_patch_activity_setting_with_missing_parameter_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        kind = 'task-added-or-reassigned'

        url = '{}/@notification-settings/activities/{}'.format(self.portal.absolute_url(), kind)
        with browser.expect_http_error(400):
            browser.open(url, method='PATCH',
                         headers=self.api_headers)
        self.assertEqual(
            {"message": "Missing parameter badge, digest or mail",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_patch_activity_setting_with_wrong_format_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        kind = 'task-added-or-reassigned'

        url = '{}/@notification-settings/activities/{}'.format(self.portal.absolute_url(), kind)
        with browser.expect_http_error(400):
            browser.open(url, method='PATCH',
                         data=json.dumps({u'mail': ['task_issuer']}),
                         headers=self.api_headers)
        self.assertEqual(
            {"message": "[('mail', WrongType([u'task_issuer'], <type 'dict'>, 'mail'))]",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_patch_general_setting_with_missing_parameter_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        setting_id = 'notify_own_actions'

        url = '{}/@notification-settings/general/{}'.format(self.portal.absolute_url(), setting_id)
        with browser.expect_http_error(400):
            browser.open(url, method='PATCH',
                         headers=self.api_headers)
        self.assertEqual(
            {"message": "Missing parameter value",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_patch_notification_setting_with_invalid_category_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        category = 'unknown'

        url = '{}/@notification-settings/{}/task-added-or-reassigned'.format(
            self.portal.absolute_url(), category)
        with browser.expect_http_error(400):
            browser.open(url, method='PATCH',
                         headers=self.api_headers)
        self.assertEqual(
            {"message": "'{}' does not exist".format(category),
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_patch_setting_with_wrong_number_of_path_params_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@notification-settings/general'.format(self.portal.absolute_url())
        with browser.expect_http_error(400):
            browser.open(url, method='PATCH',
                         headers=self.api_headers)
        self.assertEqual(
            {"message": "Must supply setting category and setting ID as URL path parameters",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_patch_general_setting_for_pure_plone_user_raises_bad_request(self, browser):
        self.login(self.manager, browser)
        self.assertIsNone(self.get_ogds_user(self.manager))
        setting_id = 'notify_own_actions'
        url = '{}/@notification-settings/general/{}'.format(self.portal.absolute_url(), setting_id)
        with browser.expect_http_error(400):
            browser.open(url, method='PATCH',
                         data=json.dumps({u'value': True}),
                         headers=self.api_headers)

        self.assertEqual(browser.json['message'],
                         "User {} not found in OGDS".format(self.manager.getId()))
        self.assertEqual(browser.json['type'], 'BadRequest')

    @browsing
    def test_respects_prefer_header(self, browser):
        self.login(self.regular_user, browser)
        kind = 'added-as-watcher'
        headers = self.api_headers.copy()
        headers.update({'Prefer': 'return=representation'})

        url = '{}/@notification-settings/activities/{}'.format(self.portal.absolute_url(), kind)
        browser.open(url, method='PATCH',
                     data=json.dumps({"reset": True}),
                     headers=headers)

        self.assertEquals(200, browser.status_code)
        self.assertEquals(
            {u'@id': url,
             u'badge': {u'always': True},
             u'digest': {u'always': False},
                u'group': u'general',
                u'id': kind,
                u'kind': kind,
                u'mail': {u'always': False},
                u'personal': False,
                u'title': u'Added as watcher'},
            browser.json)
