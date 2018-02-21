from opengever.activity.hooks import DEFAULT_SETTINGS
from opengever.activity.model.settings import NotificationDefault
from opengever.testing import IntegrationTestCase


class TestNotificationDefaultsHook(IntegrationTestCase):

    def test_notification_default(self):
        # only check task-added default as a sample
        default = NotificationDefault.query.by_kind('task-added').first()
        self.assertEquals(
            frozenset([u'task_issuer', u'task_responsible']),
            default.badge_notification_roles)
        self.assertEquals(frozenset([u'task_responsible']),
                          default.mail_notification_roles)
