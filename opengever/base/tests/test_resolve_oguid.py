from ftw.testbrowser import browsing
from opengever.base.browser.resolveoguid import ResolveOGUIDView
from opengever.base.oguid import Oguid
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase


class TestResolveOGUIDView(IntegrationTestCase):

    def setUp(self):
        super(TestResolveOGUIDView, self).setUp()

    @browsing
    def test_check_permissions_fails_with_nobody(self, browser):
        self.login(self.regular_user)
        url = ResolveOGUIDView.url_for(
            Oguid.for_object(self.task), get_current_admin_unit())

        with browser.expect_unauthorized():
            browser.open(url)

    @browsing
    def test_redirect_if_correct_client(self, browser):
        self.login(self.regular_user, browser=browser)

        url = ResolveOGUIDView.url_for(
            Oguid.for_object(self.task), get_current_admin_unit())

        browser.open(url)
        self.assertEqual(self.task.absolute_url(), browser.url)
