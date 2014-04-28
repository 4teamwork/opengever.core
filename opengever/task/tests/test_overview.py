from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import set_current_client_id
from plone.app.testing import TEST_USER_ID


class TestTaskOverview(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestTaskOverview, self).setUp()
        create_ogds_user(TEST_USER_ID)
        create_client(clientid="client1")
        set_current_client_id(self.portal, clientid="client1")

    def test_issuer_is_linked_to_issuers_details_view(self):
        task = create(Builder("task").having(issuer=TEST_USER_ID))
        self.browser.open(
            '%s/tabbedview_view-overview' % task.absolute_url())

        link = self.browser.locate('.issuer a')
        self.assertEquals(
            'http://nohost/plone/@@user-details/test_user_1_',
            link.target.get('href'))

    def test_issuer_is_labeld_by_user_description(self):
        task = create(Builder("task").having(issuer=TEST_USER_ID))
        self.browser.open(
            '%s/tabbedview_view-overview' % task.absolute_url())

        link = self.browser.locate('.issuer a')
        self.assertEquals(
            'Boss Hugo (test_user_1_)', link.plain_text())

    def test_issuer_is_prefixed_by_current_client_title_and_slash_on_a_multiclient_setup(self):
        client2 = create_client(clientid="client2")
        task = create(Builder("task").having(issuer=TEST_USER_ID))

        self.browser.open(
            '%s/tabbedview_view-overview' % task.absolute_url())

        td = self.browser.locate('.issuer')
        self.assertEquals(
            'Client1 / Boss Hugo (test_user_1_)', td.plain_text())

    def test_issuer_is_prefixed_by_predecessor_client_title_on_a_forwarding_successor(self):
        client2 = create_client(clientid="client2")

        forwarding = create(Builder('forwarding').having(issuer=TEST_USER_ID))
        successor = create(Builder('task')
                           .having(issuer=TEST_USER_ID)
                           .successor_from(forwarding))
        self.browser.open(
            '%s/tabbedview_view-overview' % successor.absolute_url())

        link = self.browser.locate('.issuer')
        self.assertEquals(
            'Client1 / Boss Hugo (test_user_1_)', link.plain_text())
