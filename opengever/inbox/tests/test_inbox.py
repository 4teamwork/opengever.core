from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import add_languages
from opengever.testing import FunctionalTestCase
from plone import api
import transaction


class TestInbox(FunctionalTestCase):

    def setUp(self):
        super(TestInbox, self).setUp()

        self.org_unit2 = create(Builder('org_unit').id('client2')
                                .having(admin_unit=self.admin_unit))

    def test_get_responsible_org_unit_fetch_configured_org_unit(self):
        inbox = create(Builder('inbox').
                       having(responsible_org_unit='client1'))

        self.assertEqual(self.org_unit, inbox.get_responsible_org_unit())

    def test_get_responsible_org_unit_returns_none_when_no_org_unit_is_configured(self):
        inbox = create(Builder('inbox'))

        self.assertEqual(None, inbox.get_responsible_org_unit())

    def test_get_sequence_number_returns_none(self):
        inbox = create(Builder('inbox'))

        self.assertEqual(None, inbox.get_sequence_number())
        transaction.commit()

    @browsing
    def test_supports_translated_title(self, browser):
        add_languages(['de-ch', 'fr-ch'])

        browser.login().open()
        factoriesmenu.add('Inbox')
        browser.fill({'Title (German)': u'Eingangskorb',
                      'Title (French)': u'Bo\xeete de r\xe9ception'})
        browser.find('Save').click()

        browser.find('FR').click()
        self.assertEquals(u'Bo\xeete de r\xe9ception',
                          browser.css('h1').first.text)

        browser.find('DE').click()
        self.assertEquals(u'Eingangskorb',
                          browser.css('h1').first.text)
