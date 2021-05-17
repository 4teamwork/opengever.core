from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.inbox.container import IInboxContainer
from opengever.testing import add_languages
from opengever.testing import FunctionalTestCase
from unittest import skip


class TestInboxContainer(FunctionalTestCase):

    @browsing
    def test_adding(self, browser):
        self.grant('Manager')
        add_languages(['de-ch'])
        browser.login().open()
        factoriesmenu.add('Inbox Container')
        browser.fill({'Title (German)': u'Eingangsk\xf6rbe',
                      'Title (English)': u'Inbox Container'}).save()

        statusmessages.assert_no_error_messages()
        self.assertTrue(IInboxContainer.providedBy(browser.context))

    @browsing
    def test_is_only_addable_by_manager(self, browser):
        browser.login().open()

        self.grant('Administrator')
        browser.reload()
        self.assertNotIn(
            'Inbox Container',
            factoriesmenu.addable_types()
            )

        self.grant('Manager')
        browser.reload()
        self.assertIn(
            'Inbox Container',
            factoriesmenu.addable_types()
            )

    @browsing
    def test_portlet_inheritance_is_blocked(self, browser):
        self.grant('Manager')
        add_languages(['de-ch'])
        browser.login().open()
        factoriesmenu.add('Inbox Container')
        browser.fill({'Title (German)': u'Eingangsk\xf6rbe',
                      'Title (English)': u'Inbox Container'}).save()

        statusmessages.assert_no_error_messages()
        self.assert_portlet_inheritance_blocked(
            'plone.leftcolumn', browser.context)


class TestInboxView(FunctionalTestCase):

    def setUp(self):
        super(TestInboxView, self).setUp()
        self.container = create(Builder('inbox_container').titled(u'Inboxes'))

    @browsing
    def test_redirects_to_current_inbox_when_accessing_inbox_container(self, browser):
        self.client1_inbox = create(
            Builder('inbox')
            .titled(u'Org Unit 1 Inbox')
            .within(self.container)
            .having(responsible_org_unit='org-unit-1'))

        browser.login().open(self.container)

        self.assertEqual(self.client1_inbox.absolute_url(), browser.url)

    @browsing
    def test_stays_on_inbox_container_when_current_inbox_not_available(self, browser):
        self.client2_inbox = create(
            Builder('inbox')
            .titled(u'Org Unit 2 Inbox')
            .within(self.container)
            .having(responsible_org_unit='org-unit-2'))

        browser.login().open(self.container)
        self.assertEqual(self.container.absolute_url(), browser.url)
        self.assertEquals(
            ["You're not allowed to access the inbox of Org Unit 1."],
            statusmessages.messages().get('warning'))

    @skip("This test currently fails in a flaky way on CI."
          "See https://github.com/4teamwork/opengever.core/issues/3995")
    @browsing
    def test_supports_translated_title(self, browser):
        add_languages(['de-ch', 'fr-ch'])
        self.grant('Manager')

        browser.login().open()
        factoriesmenu.add('Inbox Container')
        browser.fill({'Title (German)': u'Eingangskorb',
                      'Title (French)': u'Bo\xeete de r\xe9ception'})
        browser.find('Save').click()

        browser.find(u'Fran\xe7ais').click()
        self.assertEquals(u'Bo\xeete de r\xe9ception',
                          browser.css('h1').first.text)

        browser.find('Deutsch').click()
        self.assertEquals(u'Eingangskorb',
                          browser.css('h1').first.text)
