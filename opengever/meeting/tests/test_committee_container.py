from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.testing import add_languages
from opengever.testing import IntegrationTestCase
from unittest import skip


class TestCommitteeContainer(IntegrationTestCase):

    features = ('meeting',)

    @skip("This test currently fails in a flaky way on CI."
          "See https://github.com/4teamwork/opengever.core/issues/3995")
    @browsing
    def test_supports_translated_title(self, browser):
        self.login(self.manager, browser)
        add_languages(['de-ch', 'fr-ch'])
        browser.open()
        factoriesmenu.add('Committee Container')
        browser.fill({'Title (German)': u'Sitzungen',
                      'Title (French)': u's\xe9ance'}).save()
        statusmessages.assert_no_error_messages()

        browser.find(u'Fran\xe7ais').click()
        self.assertEquals(u's\xe9ance', browser.css('h1').first.text)

        browser.find('Deutsch').click()
        self.assertEquals(u'Sitzungen', browser.css('h1').first.text)


    def test_portlets_inheritance_is_blocked(self):
        self.login(self.manager)
        self.assert_portlet_inheritance_blocked(
            'plone.leftcolumn', self.committee_container)


    @browsing
    def test_visible_fields_order_in_form(self, browser):
        fields = [u'Title']
        self.login(self.manager, browser)

        browser.open()
        factoriesmenu.add('Committee Container')
        self.assertEquals(fields, filter(len, browser.css('form#form div.field > label').text))

        browser.open(self.committee_container, view='edit')
        self.assertEquals(fields, filter(len, browser.css('form#form div.field > label').text))
