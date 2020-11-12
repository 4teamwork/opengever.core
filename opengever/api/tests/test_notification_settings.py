from ftw.testbrowser import browsing
from opengever.activity import model
from opengever.activity.notification_settings import NotificationSettings
from opengever.testing import IntegrationTestCase


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
            u'badge': {u'regular_watcher': True},
            u'digest': {u'regular_watcher': False},
            u'group': u'watcher',
            u'id': u'added-as-watcher',
            u'kind': u'added-as-watcher',
            u'mail': {u'regular_watcher': False},
            u'personal': False,
            u'title': u'Added as watcher'
        }, browser.json['activities']['items'][0])

        self.assertEqual([u'added-as-watcher', u'task-added-or-reassigned',
                          u'task-transition-modify-deadline', u'task-commented',
                          u'task-status-modified', u'task-reminder', u'dossier-overdue'],
                         [activity['kind'] for activity in browser.json['activities']['items']])

        self.assertEqual({
            u'@id': u'http://nohost/plone/@notification-settings/general/notify_inbox_actions',
            u'group': u'general',
            u'help_text': u'Activate, respectively deactivate, all notifications due to your '
            u'inbox permissions.',
            u'id': u'notify_inbox_actions',
            u'personal': False,
            u'title': u'Enable notifications for inbox actions',
            u'value': True
        }, browser.json['general']['items'][-1])

        self.assertEqual([u'notify_own_actions', u'notify_inbox_actions'],
                         [activity['id'] for activity in browser.json['general']['items']])

        self.assertEqual([
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
                                u'workspace_member_role': True},
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
                                 u'workspace_member_role': True},
                     u'group': u'workspace',
                     u'id': u'todo-modified',
                     u'kind': u'todo-modified',
                     u'mail': {u'todo_responsible_role': False,
                               u'workspace_member_role': False},
                     u'personal': False,
                     u'title': u'ToDo modified'}]},
            u'general': {
                u'@id': u'http://nohost/plone/@notification-settings/general',
                u'items': [{
                    u'@id': u'http://nohost/plone/@notification-settings/general/notify_own_actions',
                    u'group': u'general',
                    u'help_text': u"By default no notifications are emitted for a users'own "
                                  u"actions. This option allows to modify this behavior. "
                                  u"Notwithstanding this configuration, user notification settings "
                                  u"for each action type will get applied anyway.",
                    u'id': u'notify_own_actions',
                    u'personal': False,
                    u'title': u'Enable notifications for own actions',
                    u'value': False}]},
            u'translations': [{
                u'id': u'todo_responsible_role',
                u'title': u'ToDo responsible'},
                {u'id': u'workspace_member_role',
                 u'title': u'Workspace member'}]}, browser.json)
