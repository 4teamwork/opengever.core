from opengever.base.config_checks.checks import BaseCheck
from opengever.base.config_checks.manager import ConfigCheckManager
from opengever.base.interfaces import IConfigCheck
from opengever.testing import IntegrationTestCase
from zope.component import adapter
from zope.component import getSiteManager
from zope.interface import implementer
from zope.interface import Interface


@implementer(IConfigCheck)
@adapter(Interface)
class DummyCheckMissconfigured1(BaseCheck):
    def check(self):
        return self.config_error(title="Dummy check 1", description="Description 1")


@implementer(IConfigCheck)
@adapter(Interface)
class DummyCheckMissconfigured2(BaseCheck):
    def check(self):
        return self.config_error(title="Dummy check 2")


class TestConfigCheckManager(IntegrationTestCase):

    def test_check_all_returns_an_empty_list_if_everything_is_ok(self):
        self.login(self.manager)
        self.assertEqual([], ConfigCheckManager().check_all())

    def test_check_all_returns_an_error_dict_for_each_failing_check(self):
        self.login(self.manager)
        getSiteManager().registerAdapter(DummyCheckMissconfigured1, name="check-missconfigured-1")
        getSiteManager().registerAdapter(DummyCheckMissconfigured2, name="check-missconfigured-2")

        self.assertItemsEqual([
            {'id': 'DummyCheckMissconfigured1', 'title': 'Dummy check 1', 'description': 'Description 1'},
            {'id': 'DummyCheckMissconfigured2', 'title': 'Dummy check 2', 'description': ''}
        ], ConfigCheckManager().check_all())
