from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestTaskOverview(FunctionalTestCase):

    def setUp(self):
        super(TestTaskOverview, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

    @browsing
    def test_issuer_is_linked_to_issuers_details_view(self, browser):
        task = create(Builder("task").having(issuer=TEST_USER_ID))

        browser.login().open(task, view='tabbedview_view-overview')

        self.assertEquals(
            'http://nohost/plone/@@user-details/test_user_1_',
            browser.css('.issuer a').first.get('href'))

    @browsing
    def test_issuer_is_labeld_by_user_description(self, browser):
        task = create(Builder("task").having(issuer=TEST_USER_ID))

        browser.login().open(task, view='tabbedview_view-overview')

        self.assertEquals(
            self.user.label(), browser.css('.issuer a').first.text)

    @browsing
    def test_issuer_is_prefixed_by_current_org_unit_on_a_multiclient_setup(self, browser):
        create(Builder('org_unit').id('client2'))
        task = create(Builder("task").having(issuer=TEST_USER_ID))

        browser.login().open(task, view='tabbedview_view-overview')

        self.assertEquals(
            'Client1 / User Test (test_user_1_)',
            browser.css('.issuer').first.text)

    @browsing
    def test_issuer_is_prefixed_by_predecessor_org_unit_on_a_forwarding_successor(self, browser):
        create(Builder('org_unit').id('client2'))
        forwarding = create(Builder('forwarding').having(issuer=TEST_USER_ID))
        successor = create(Builder('task')
                           .having(issuer=TEST_USER_ID,
                                   responsible_client='client2')
                           .successor_from(forwarding))

        browser.login().open(successor, view='tabbedview_view-overview')

        self.assertEquals(
            'Client2 / User Test (test_user_1_)',
            browser.css('.issuer').first.text)
