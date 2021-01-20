from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase


class TestSelfRegistration(IntegrationTestCase):

    features = ('workspace',)

    @browsing
    def test_self_registration_redirects_to_root(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.allow_redirects = False
        browser.open(self.portal.absolute_url() + '/@@user-self-registration')
        self.assertEqual(browser.headers['Location'], self.portal.absolute_url())

    @browsing
    def test_self_registration_redirects_to_next(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.allow_redirects = False
        browser.open(
            self.portal.absolute_url() + '/@@user-self-registration?next=/workspaces')
        self.assertEqual(
            browser.headers['Location'],
            self.portal.absolute_url() + '/workspaces',
        )

    @browsing
    def test_self_registration_creates_ogds_user(self, browser):
        user = create(
            Builder('user')
            .having(firstname='Hugo', lastname='Boss')
            .with_userid('hugo.boss'))

        self.login(user, browser=browser)
        browser.allow_redirects = False
        browser.open(self.portal.absolute_url() + '/@@user-self-registration')

        self.assertIsNotNone(ogds_service().fetch_user('hugo.boss'))

    @browsing
    def test_self_registration_creates_ogds_user_with_groups(self, browser):
        user = create(Builder('user')
                      .with_userid('hugo.boss')
                      .having(firstname='Hugo', lastname='Boss')
                      .in_groups('fa_users'))

        self.login(user, browser=browser)
        browser.allow_redirects = False
        browser.open(self.portal.absolute_url() + '/@@user-self-registration')

        group = ogds_service().fetch_group('fa_users')
        self.assertIn('hugo.boss', [u.userid for u in group.users])
