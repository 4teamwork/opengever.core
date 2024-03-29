from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing import IntegrationTestCase


class TestAllowedRolesAndPrincipalsAPI(IntegrationTestCase):
    maxDiff = None

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
        url = '{}/@allowed-roles-and-principals'.format(self.dossier.absolute_url())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        allowed_roles_and_principals = {
            u'Administrator',
            u'Editor',
            u'LimitedAdmin',
            u'Manager',
            u'Reader',
            u'Contributor',
            u'TaskResponsible',
            u'principal:fa_inbox_users',
            u'principal:fa_users',
            u'principal:%s' % self.archivist.getId(),
            u'principal:%s' % self.regular_user.getId(),
        }
        self.assertEqual(url, browser.json['@id'])
        self.assertEqual(allowed_roles_and_principals,
                         set(browser.json['allowed_roles_and_principals']))
        self.assertNotIn(u'principal:%s' % self.dossier_responsible.getId(),
                         browser.json.get('allowed_roles_and_principals'))

        RoleAssignmentManager(self.dossier).add_or_update_assignment(
            SharingRoleAssignment(self.dossier_responsible.getId(), ['Reader']))
        browser.open(self.dossier.absolute_url() + '/@allowed-roles-and-principals',
                     method='GET', headers={'Accept': 'application/json'})

        self.assertIn(u'principal:%s' % self.dossier_responsible.getId(), browser.json.get('allowed_roles_and_principals'))
