from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase


class TestContact(SolrIntegrationTestCase):

    @browsing
    def test_can_add_a_contact(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.contactfolder)
        factoriesmenu.add('Contact')
        browser.fill({'First name': 'Hanspeter',
                      'Last name': 'D\xc3\xbcrr'})
        browser.find('Save').click()

        self.assertEqual(
            'http://nohost/plone/kontakte/durr-hanspeter-1/contact_view',
            browser.url)
        self.assertEqual(u'D\xfcrr Hanspeter', browser.css('h1').first.text)

    @browsing
    def test_edit_a_contact(self, browser):
        self.login(self.regular_user)

        browser.login().open(self.hanspeter_duerr, view='edit')
        browser.fill({'Last name': 'Walter'})
        browser.find('Save').click()

        self.assertEqual('Walter Hanspeter', browser.css('h1').first.text)

    def test_searchable_text(self):
        self.login(self.regular_user)
        self.assertEqual(u'D\xfcrr Hanspeter',
                         solr_data_for(self.hanspeter_duerr, 'SearchableText'))
