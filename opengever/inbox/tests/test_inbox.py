from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestInbox(FunctionalTestCase):

    def setUp(self):
        super(TestInbox, self).setUp()

        self.org_unit2 = create(Builder('org_unit').id('client2')
                                .having(admin_unit=self.admin_unit))

    def test_get_current_inbox_returns_sub_inbox_assigned_to_current_org_unit(self):
        inbox = create(Builder('inbox'))
        create(Builder('inbox')
               .within(inbox)
               .having(responsible_org_unit='client2'))
        sub1 = create(Builder('inbox')
                      .within(inbox)
                      .having(responsible_org_unit='client1'))

        self.assertEquals(sub1, inbox.get_current_inbox())

    def test_get_current_inbox_returns_object_itself_when_no_subinbox_is_found(self):
        inbox = create(Builder('inbox'))
        create(Builder('inbox')
               .within(inbox)
               .having(responsible_org_unit='client2'))
        create(Builder('inbox')
               .within(inbox)
               .having(responsible_org_unit='client3'))

        self.assertEquals(inbox, inbox.get_current_inbox())

    def test_inbox_is_main_when_root_inbox_and_not_assigned_to_orgunit(self):
        assigned_inbox = create(Builder('inbox')
                                .having(responsible_org_unit='client1'))
        sub_inbox = create(Builder('inbox').within(assigned_inbox))
        main_inbox = create(Builder('inbox'))

        self.assertFalse(assigned_inbox.is_main_inbox())
        self.assertFalse(sub_inbox.is_main_inbox())
        self.assertTrue(main_inbox.is_main_inbox())

    def test_get_responsible_org_unit_fetch_configured_org_unit(self):
        inbox = create(Builder('inbox').
                       having(responsible_org_unit='client1'))

        self.assertEqual(self.org_unit, inbox.get_responsible_org_unit())

    def test_get_responsible_org_unit_returns_none_when_no_org_unit_is_configured(self):
        inbox = create(Builder('inbox'))

        self.assertEqual(None, inbox.get_responsible_org_unit())


class TestInboxView(FunctionalTestCase):

    def setUp(self):
        super(TestInboxView, self).setUp()

        self.main_inbox = create(Builder('inbox')
                                 .titled(u'Main Inbox'))

    @browsing
    def test_redirects_to_current_inbox_when_accessing_main_inbox(self, browser):
        self.client1_inbox = create(Builder('inbox')
                                    .titled(u'Client1 Inbox')
                                    .within(self.main_inbox)
                                    .having(responsible_org_unit='client1'))

        browser.login().open(self.main_inbox)

        self.assertEqual(self.client1_inbox.absolute_url(), browser.url)

    @browsing
    def test_stay_on_main_inbox_when_no_current_inbox_exists(self, browser):
        self.client1_inbox = create(Builder('inbox')
                            .titled(u'Client1 Inbox')
                            .within(self.main_inbox)
                            .having(responsible_org_unit='client2'))

        browser.login().open(self.main_inbox)
        self.assertEqual(self.main_inbox.absolute_url(), browser.url)
