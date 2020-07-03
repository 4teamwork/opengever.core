from ftw.testbrowser import browsing
from opengever.setup.casauth import install_cas_auth_plugin
from opengever.testing import IntegrationTestCase
from plone import api


class TestLogoutUserEndpointWithoutCAS(IntegrationTestCase):

    @browsing
    def test_logout_deletes_ac_cookie(self, browser):
        driver = browser.get_driver()

        with self.login(self.regular_user, browser=browser):
            dossier_url = self.dossier.absolute_url()
            portal_url = self.portal.absolute_url()

        # Check that we cannot access the dossier
        with browser.expect_unauthorized():
            browser.open(dossier_url, headers=self.api_headers)

        # set __ac cookie
        with self.login(self.regular_user, browser=browser):
            self.portal.acl_users.credentials_cookie_auth.login()
            driver.requests_session.cookies.set(
                '__ac', self.request.response.cookies['__ac'].get('value'))

        # Check that we can access the dossier
        browser.open(dossier_url, headers=self.api_headers)
        self.assertEqual(200, self.request.response.getStatus())

        # logout
        browser.open(portal_url + '/@logout',
                     method='POST', headers=self.api_headers)
        self.assertEqual(200, self.request.response.getStatus())

        # check that cookie gets invalidated
        self.assertEqual(
            {'__ac': {
                'expires': 'Wed, 31-Dec-97 23:59:59 GMT',
                'max_age': 0,
                'path': '/',
                'quoted': True,
                'value': 'deleted'}},
            driver.response.cookies)

        # Check that we cannot access the dossier anymore once the cookie is deleted
        driver.requests_session.cookies.set(
            '__ac', driver.response.cookies['__ac'].get('value'))
        with browser.expect_unauthorized():
            browser.open(dossier_url, headers=self.api_headers)


class TestLogoutUserEndpointWithCASAuth(IntegrationTestCase):

    def setUp(self):
        super(TestLogoutUserEndpointWithCASAuth, self).setUp()
        install_cas_auth_plugin('portal')

    def tearDown(self):
        super(TestLogoutUserEndpointWithCASAuth, self).tearDown()
        acl_users = api.portal.get_tool('acl_users')
        acl_users.plugins.removePluginById('cas_auth')

    @browsing
    def test_logout_deletes_ac_cookie(self, browser):
        driver = browser.get_driver()

        with self.login(self.regular_user, browser=browser):
            dossier_url = self.dossier.absolute_url()
            portal_url = self.portal.absolute_url()

        # Check that we cannot access the dossier
        with browser.expect_unauthorized():
            browser.open(dossier_url, headers=self.api_headers)

        # set __ac cookie
        with self.login(self.regular_user, browser=browser):
            self.portal.acl_users.credentials_cookie_auth.login()
            driver.requests_session.cookies.set(
                '__ac', self.request.response.cookies['__ac'].get('value'))

        # Check that we can access the dossier
        browser.open(dossier_url, headers=self.api_headers)
        self.assertEqual(200, self.request.response.getStatus())

        # logout
        browser.open(portal_url + '/@logout',
                     method='POST', headers=self.api_headers)
        self.assertEqual(200, self.request.response.getStatus())

        # check that cookie gets invalidated
        self.assertEqual(
            {'__ac': {
                'expires': 'Wed, 31-Dec-97 23:59:59 GMT',
                'max_age': 0,
                'path': '/',
                'quoted': True,
                'value': 'deleted'}},
            driver.response.cookies)

        # Check that we cannot access the dossier anymore once the cookie is deleted
        driver.requests_session.cookies.set(
            '__ac', driver.response.cookies['__ac'].get('value'))
        with browser.expect_unauthorized():
            browser.open(dossier_url, headers=self.api_headers)

    @browsing
    def test_logout_deletes_all_ac_cookies_when_using_custom_cookie_name(self, browser):
        driver = browser.get_driver()

        with self.login(self.regular_user, browser=browser):
            dossier_url = self.dossier.absolute_url()
            portal_url = self.portal.absolute_url()

        # Check that we cannot access the dossier
        with browser.expect_unauthorized():
            browser.open(dossier_url, headers=self.api_headers)

        # Customize cookie name, like we do in production
        self.portal.acl_users.session.cookie_name = '__ac_fd'

        # set custom __ac_fd cookie
        with self.login(self.regular_user, browser=browser):
            self.portal.acl_users.credentials_cookie_auth.login()
            driver.requests_session.cookies.set(
                '__ac_fd', self.request.response.cookies['__ac_fd'].get('value'))

        # Check that we can access the dossier
        browser.open(dossier_url, headers=self.api_headers)
        self.assertEqual(200, self.request.response.getStatus())

        # logout
        browser.open(portal_url + '/@logout',
                     method='POST', headers=self.api_headers)
        self.assertEqual(200, self.request.response.getStatus())

        # check that cookies gets invalidated
        self.assertEqual(
            {'__ac': {
                'expires': 'Wed, 31-Dec-97 23:59:59 GMT',
                'max_age': 0,
                'path': '/',
                'quoted': True,
                'value': 'deleted'},
             '__ac_fd': {
                'expires': 'Wed, 31-Dec-97 23:59:59 GMT',
                'max_age': 0,
                'path': '/',
                'quoted': True,
                'value': 'deleted'}},
            driver.response.cookies)

        # Check that we cannot access the dossier anymore once the cookie is deleted
        driver.requests_session.cookies.set(
            '__ac_fd', driver.response.cookies['__ac'].get('value'))
        with browser.expect_unauthorized():
            browser.open(dossier_url, headers=self.api_headers)


class TestLogoutUserEndpointWithJWTToken(IntegrationTestCase):

    @browsing
    def test_logout_succeeds(self, browser):
        with self.login(self.regular_user, browser=browser):
            dossier_url = self.dossier.absolute_url()
            portal_url = self.portal.absolute_url()

        # Check that we cannot access the dossier
        with browser.expect_unauthorized():
            browser.open(dossier_url, headers=self.api_headers)

        # Authorize with JWT token
        self.portal.acl_users.jwt_auth.store_tokens = True
        token = self.portal.acl_users.jwt_auth.create_token(self.regular_user.id)
        browser.append_request_header('Authorization', "Bearer {}".format(token))

        # Check that we can access the dossier
        browser.open(dossier_url, headers=self.api_headers)
        self.assertEqual(200, self.request.response.getStatus())

        # logout
        browser.open(portal_url + '/@logout',
                     method='POST', headers=self.api_headers)
        self.assertEqual(200, self.request.response.getStatus())

        # Check that we cannot access the dossier anymore
        with browser.expect_unauthorized():
            browser.open(dossier_url, headers=self.api_headers)

    @browsing
    def test_logout_raises_error_when_tokens_are_not_stored_on_server(self, browser):
        with self.login(self.regular_user, browser=browser):
            dossier_url = self.dossier.absolute_url()
            portal_url = self.portal.absolute_url()

        # Authorize with JWT token
        token = self.portal.acl_users.jwt_auth.create_token(self.regular_user.id)
        browser.append_request_header('Authorization', "Bearer {}".format(token))

        # logout
        with browser.expect_http_error(501):
            browser.open(portal_url + '/@logout',
                         method='POST', headers=self.api_headers)

        # Check that we can still access the dossier
        browser.open(dossier_url, headers=self.api_headers)
        self.assertEqual(200, self.request.response.getStatus())
