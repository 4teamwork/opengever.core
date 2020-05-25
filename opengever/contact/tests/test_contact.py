from ftw.testbrowser import browsing
from ftw.testbrowser import InsufficientPrivileges
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase


class TestContact(SolrIntegrationTestCase):

    features = ('contact', )

    @browsing
    def test_cannot_add_a_contact_with_contact_feature_enabled(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.contactfolder)

        with self.assertRaises(ValueError) as err:
            factoriesmenu.addable_types()

        self.assertEqual(
            'Factories menu is not visible.',
            str(err.exception))

        with self.assertRaises(InsufficientPrivileges):
            browser.visit(self.contactfolder, view="++add++opengever.contact.contact")

    @browsing
    def test_can_add_a_contact_with_contact_feature_disabled(self, browser):
        self.login(self.regular_user, browser)
        self.deactivate_feature('contact')

        browser.open(self.contactfolder)
        factoriesmenu.add('Contact')
        browser.fill({'Firstname': 'Hanspeter',
                      'Lastname': 'D\xc3\xbcrr'})
        browser.find('Save').click()

        self.assertEqual(
            'http://nohost/plone/kontakte/durr-hanspeter-1/contact_view',
            browser.url)
        self.assertEqual(u'D\xfcrr Hanspeter', browser.css('h1').first.text)

    @browsing
    def test_edit_a_contact(self, browser):
        self.login(self.regular_user)

        browser.login().open(self.hanspeter_duerr, view='edit')
        browser.fill({'Lastname': 'Walter'})
        browser.find('Save').click()

        self.assertEqual('Walter Hanspeter', browser.css('h1').first.text)

    def test_searchable_text(self):
        self.login(self.regular_user)
        self.assertEqual(u'D\xfcrr Hanspeter',
                          solr_data_for(self.hanspeter_duerr, 'SearchableText'))
