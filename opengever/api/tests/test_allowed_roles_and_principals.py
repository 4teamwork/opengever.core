from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing import IntegrationTestCase


class TestAllowedRolesAndPrincipalsAPI(IntegrationTestCase):

    @browsing
    def test_raises_unauthorized_when_user_accessing_allowed_roles_and_principals(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_unauthorized():
            browser.open(self.document.absolute_url() + '/@allowed-roles-and-principals',
                         method='GET', headers={'Accept': 'application/json'})
        self.assertEqual(401, browser.status_code)

    @browsing
    def test_get_returns_allowed_roles_and_principals(self, browser):
        self.login(self.service_user, browser)
        browser.open(self.dossier.absolute_url() + '/@allowed-roles-and-principals',
                     method='GET', headers={'Accept': 'application/json'})

        excepted_json = {
            u'allowed_roles_and_principals': [
                u'principal:fa_inbox_users',
                u'Administrator',
                u'principal:fa_users',
                u'principal:kathi.barfuss',
                u'Manager',
                u'Editor',
                u'Reader',
                u'Contributor'],
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen'
                    u'/dossier-1/@allowed-roles-and-principals'}

        self.assertEquals(excepted_json, browser.json)
        self.assertNotIn(u'principal:robert.ziegler',
                         browser.json.get('allowed_roles_and_principals'))

        RoleAssignmentManager(self.dossier).add_or_update_assignment(
            SharingRoleAssignment(self.dossier_responsible.getId(), ['Reader']))
        browser.open(self.dossier.absolute_url() + '/@allowed-roles-and-principals',
                     method='GET', headers={'Accept': 'application/json'})

        self.assertIn(u'principal:robert.ziegler', browser.json.get('allowed_roles_and_principals'))
