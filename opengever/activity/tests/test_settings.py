from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.hooks import DEFAULT_SETTINGS
from opengever.activity.model.settings import NotificationSetting
from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.testing import IntegrationTestCase
import json


class TestListSettings(IntegrationTestCase):

    features = ('activity', )

    @browsing
    def test_list_all_settings(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='notification-settings/list')

        activities = browser.json.get('activities')
        self.assertEquals(
            [item.get('kind') for item in activities],
            [item.get('kind') for item in DEFAULT_SETTINGS])

        task_added = [item for item in activities if item.get('kind') == 'task-added'][0]
        self.assertEquals({u'task_issuer': False, u'task_responsible': True},
                          task_added['mail'])
        self.assertEquals({u'task_issuer': False, u'task_responsible': False},
                          task_added['badge'])
        self.assertEquals('default', task_added['setting_type'])

    @browsing
    def test_list_returns_personal_setting_if_exists(self, browser):
        create(Builder('notification_setting')
               .having(kind='task-transition-open-in-progress',
                       userid=self.regular_user.getId(),
                       mail_notification_roles=[TASK_RESPONSIBLE_ROLE],
                       badge_notification_roles=[TASK_ISSUER_ROLE,
                                                 TASK_RESPONSIBLE_ROLE]))

        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='notification-settings/list')

        activities = browser.json.get('activities')
        accept = [
            item for item in activities
            if item.get('kind') == 'task-transition-open-in-progress'][0]

        self.assertEquals({u'task_issuer': False, u'task_responsible': True},
                          accept['mail'])
        self.assertEquals({u'task_issuer': True, u'task_responsible': True},
                          accept['badge'])
        self.assertEquals('personal', accept['setting_type'])


class TestSaveSettings(IntegrationTestCase):

    features = ('activity', )

    data = {'kind': 'task-added',
            'mail': json.dumps([TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]),
            'badge': json.dumps([TASK_ISSUER_ROLE])}

    @browsing
    def test_save_setting_raises_keyerror_when_parameter_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(503):
            browser.open(
                self.portal, view='notification-settings/save',
                data={key: self.data[key] for key in self.data if key != 'kind'})

        with browser.expect_http_error(503):
            browser.open(
                self.portal, view='notification-settings/save',
                data={key: self.data[key] for key in self.data if key != 'mail'})

        with browser.expect_http_error(503):
            browser.open(
                self.portal, view='notification-settings/save',
                data={key: self.data[key] for key in self.data if key != 'badge'})

    @browsing
    def test_save_setting_adds_personal_setting(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal, view='notification-settings/save', data=self.data)

        settings = NotificationSetting.query.filter_by(userid=self.regular_user.getId()).all()
        self.assertEquals(1, len(settings))

        self.assertEquals('task-added', settings[0].kind)
        self.assertEquals(frozenset([TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]),
                          settings[0].mail_notification_roles)
        self.assertEquals(frozenset([TASK_ISSUER_ROLE]),
                          settings[0].badge_notification_roles)

    @browsing
    def test_save_updates_personal_setting_when_exists(self, browser):
        create(Builder('notification_setting')
               .having(kind='task-added',
                       userid=self.regular_user.getId(),
                       mail_notification_roles=[],
                       badge_notification_roles=[]))

        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='notification-settings/save', data=self.data)

        settings = NotificationSetting.query.filter_by(userid=self.regular_user.getId()).all()
        self.assertEquals(1, len(settings))

        self.assertEquals('task-added', settings[0].kind)
        self.assertEquals(frozenset([TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]),
                          settings[0].mail_notification_roles)
        self.assertEquals(frozenset([TASK_ISSUER_ROLE]),
                          settings[0].badge_notification_roles)


class TestResetSetting(IntegrationTestCase):

    features = ('activity', )

    @browsing
    def test_save_updates_personal_setting_when_exists(self, browser):
        create(Builder('notification_setting')
               .having(kind='task-added',
                       userid=self.regular_user.getId(),
                       mail_notification_roles=[],
                       badge_notification_roles=[]))

        query = NotificationSetting.query.filter_by(userid=self.regular_user.getId())
        self.assertEquals(1, query.count())

        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='notification-settings/reset',
                     data={'kind': 'task-added'})

        self.assertEquals(0, query.count())
