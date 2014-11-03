from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import FunctionalTestCase


class TestInboxView(FunctionalTestCase):

    def setUp(self):
        super(TestInboxView, self).setUp()

        self.container = create(Builder('inbox_container').titled(u'Inboxes'))

    @browsing
    def test_redirects_to_current_inbox_when_accessing_inbox_container(self, browser):
        self.client1_inbox = create(Builder('inbox')
                                    .titled(u'Client1 Inbox')
                                    .within(self.container)
                                    .having(responsible_org_unit='client1'))

        browser.login().open(self.container)

        self.assertEqual(self.client1_inbox.absolute_url(), browser.url)

    @browsing
    def test_stays_on_inbox_container_when_current_inbox_not_available(self, browser):
        self.client1_inbox = create(Builder('inbox')
                            .titled(u'Client1 Inbox')
                            .within(self.container)
                            .having(responsible_org_unit='client2'))

        browser.login().open(self.container)
        self.assertEqual(self.container.absolute_url(), browser.url)
        self.assertEquals(
            ['Your not allowed to access the inbox of Client1'],
            statusmessages.messages().get('warning'))
