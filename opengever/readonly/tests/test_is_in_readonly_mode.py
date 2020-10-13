from opengever.readonly import is_in_readonly_mode
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode


class TestIsReadonlyHelperIntegration(IntegrationTestCase):

    def test_is_in_readonly_mode_if_disabled(self):
        self.assertFalse(is_in_readonly_mode())

    def test_is_in_readonly_mode_if_enabled(self):
        with ZODBStorageInReadonlyMode():
            self.assertTrue(is_in_readonly_mode())


class TestIsReadonlyHelperFunctional(FunctionalTestCase):

    def test_is_in_readonly_mode_if_disabled(self):
        self.assertFalse(is_in_readonly_mode())

    def test_is_in_readonly_mode_if_enabled(self):
        with ZODBStorageInReadonlyMode():
            self.assertTrue(is_in_readonly_mode())
