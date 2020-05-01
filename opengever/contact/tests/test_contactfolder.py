from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.contact.interfaces import IContactFolder
from opengever.testing import add_languages
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from unittest import skip


class TestContactFolder(IntegrationTestCase):

    def setUp(self):
        super(TestContactFolder, self).setUp()
        add_languages(['de-ch', 'fr-ch'])

    def test_provides_marker_interface(self):
        self.login(self.manager)
        self.assertTrue(IContactFolder.providedBy(self.contactfolder))

    @skip("This test currently fails in a flaky way on CI."
          "See https://github.com/4teamwork/opengever.core/issues/3995")
    @browsing
    def test_supports_translated_title(self, browser):
        self.login(self.manager, browser=browser)

        browser.open()
        factoriesmenu.add('ContactFolder')
        browser.fill({'Title (German)': u'Kontakte',
                      'Title (French)': u'Contacts'})
        browser.find('Save').click()

        browser.find(u'Fran\xe7ais').click()
        self.assertEquals(u"Contacts", browser.css('h1').first.text)

        browser.find('Deutsch').click()
        self.assertEquals("Kontakte", browser.css('h1').first.text)

    def test_portlets_inheritance_is_blocked(self):
        self.login(self.manager)

        self.assert_portlet_inheritance_blocked(
            'plone.leftcolumn', self.contactfolder)


class TestLocalContactListing(SolrIntegrationTestCase):

    @browsing
    def test_list_active_contacts(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.contactfolder, view='tabbedview_view-local')

        self.assertEquals(
            [u'Lastname Firstname email Phone office',
             u'D\xfcrr Hanspeter',
             u'Meier Franz meier.f@example.com'],
            browser.css('.listing').first.rows.text)

    @browsing
    def test_administrator_has_add_team_action_visible(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.contactfolder)
        available_actions = browser.css('dd.actionMenuContent span').text
        self.assertIn('Team', available_actions)
