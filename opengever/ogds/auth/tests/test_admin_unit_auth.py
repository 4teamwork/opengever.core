from ftw.testbrowser import browsing
from opengever.ogds.auth.admin_unit import create_auth_token
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.testing import IntegrationTestCase
from plone.protect.interfaces import IDisableCSRFProtection


class TestAdminUnitAuthPlugin(IntegrationTestCase):

    def setUp(self):
        super(TestAdminUnitAuthPlugin, self).setUp()
        self.plugin = self.portal.acl_users['admin_unit_auth']
        pass

    def test_extract_credentials_without_request_header_returns_empty_dict(self):
        creds = self.plugin.extractCredentials(self.request)
        self.assertEqual(creds, {})

    def test_extract_credentials_returns_token(self):
        self.request.environ['HTTP_X_OGDS_AC'] = 'ogds-auth-token'
        creds = self.plugin.extractCredentials(self.request)
        self.assertEqual(creds, {'token': 'ogds-auth-token'})

    def test_authenticate_credentials_fails_with_wrong_extractor(self):
        creds = {
            'extractor': 'another-plugin',
            'token': create_auth_token('plone', self.regular_user.id),
        }
        ret = self.plugin.authenticateCredentials(creds)
        self.assertEqual(ret, None)

    def test_authenticate_credentials_fails_with_invalid_token(self):
        creds = {
            'extractor': self.plugin.getId(),
            'token': '123XXX',
        }
        ret = self.plugin.authenticateCredentials(creds)
        self.assertEqual(ret, None)

    def test_authenticate_credentials_fails_with_expired_token(self):
        creds = {
            'extractor': self.plugin.getId(),
            'token': create_auth_token(
                'plone', self.regular_user.id, timestamp='66508cb3'),
        }
        ret = self.plugin.authenticateCredentials(creds)
        self.assertEqual(ret, None)

    def test_authenticate_credentials_fails_with_unknown_userid(self):
        creds = {
            'extractor': self.plugin.getId(),
            'token': create_auth_token('plone', 'superuser'),
        }
        ret = self.plugin.authenticateCredentials(creds)
        self.assertEqual(ret, None)

    def test_authenticate_credentials_fails_with_unknown_admin_unit(self):
        creds = {
            'extractor': self.plugin.getId(),
            'token': create_auth_token('unitone', self.regular_user.id),
        }
        ret = self.plugin.authenticateCredentials(creds)
        self.assertEqual(ret, None)

    def test_authenticate_credentials_fails_with_invalid_signature(self):
        creds = {
            'extractor': self.plugin.getId(),
            'token': 'TB5oSjXsGRlGDfVsmFn3bdBRwiP/WdBMZFv8PxdHA6v71TxxkPzW6TE7'
                     'vs4EgVqcZB4+au74NxuqN9srQQggAjhiZTg5Njk1cGxvbmUhcmVndWxh'
                     'cl91c2Vy',
        }
        ret = self.plugin.authenticateCredentials(creds)
        self.assertEqual(ret, None)

    def test_authenticate_credentials_succeeds_with_valid_token(self):
        creds = {
            'extractor': self.plugin.getId(),
            'token': create_auth_token('plone', self.regular_user.id),
        }
        ret = self.plugin.authenticateCredentials(creds)
        self.assertEqual(
            ret, (self.regular_user.id, self.regular_user.getUserName()))

    def test_authenticate_credentials_sets_internal_request_layer(self):
        creds = {
            'extractor': self.plugin.getId(),
            'token': create_auth_token('plone', self.regular_user.id),
        }
        self.plugin.authenticateCredentials(creds)
        self.assertTrue(
            IInternalOpengeverRequestLayer.providedBy(self.request))

    def test_authenticate_credentials_disables_csrf_protection(self):
        creds = {
            'extractor': self.plugin.getId(),
            'token': create_auth_token('plone', self.regular_user.id),
        }
        self.plugin.authenticateCredentials(creds)
        self.assertTrue(
            IDisableCSRFProtection.providedBy(self.request))

    @browsing
    def test_request_with_admin_unit_auth(self, browser):
        headers = {
            'Accept': 'application/json',
            'X-OGDS-AC': create_auth_token('plone', self.regular_user.id),
        }
        browser.open(self.portal.absolute_url() + '/@config', headers=headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json['current_user'].get(u'id'), self.regular_user.id)
