from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestRoleInheritanceGet(IntegrationTestCase):

    @browsing
    def test_role_inheritance_get_falsy(self, browser):
        self.login(self.workspace_member, browser)

        browser.open(
            self.workspace_folder,
            view='@role-inheritance',
            headers=self.api_headers)
        self.assertEqual({'blocked': False}, browser.json)

    @browsing
    def test_role_inheritance_get_truthy(self, browser):
        self.login(self.administrator, browser)
        self.workspace_folder.__ac_local_roles_block__ = True

        browser.open(
            self.workspace_folder,
            view='@role-inheritance',
            headers=self.api_headers)
        self.assertEqual({'blocked': True}, browser.json)
