from ftw.testbrowser import browsing
from opengever.task import is_private_task_feature_enabled
from opengever.testing import IntegrationTestCase


class TestPrivateTaskIntegration(IntegrationTestCase):

    @browsing
    def test_feature_is_activated_by_default(self, browser):
        self.assertTrue(is_private_task_feature_enabled())


class TestPrivateTaskDeactivatedIntegration(IntegrationTestCase):

    features = ('!private-tasks', )

    @browsing
    def test_feature_is_deactivated(self, browser):
        self.assertFalse(is_private_task_feature_enabled())

