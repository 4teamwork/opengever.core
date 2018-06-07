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
                      'Title (French)': u's\xe9ance',
                      'Protocol template': self.sablon_template,
                      'Excerpt template': self.sablon_template,
                      'Table of contents template': self.sablon_template}).save()
        statusmessages.assert_no_error_messages()

        browser.find(u'Fran\xe7ais').click()
        self.assertEquals(u's\xe9ance', browser.css('h1').first.text)

        browser.find('Deutsch').click()
        self.assertEquals(u'Sitzungen', browser.css('h1').first.text)

    def test_get_toc_template(self):
        self.login(self.manager)

        self.assertIsNone(self.committee_container.toc_template)
        self.assertIsNone(self.committee_container.get_toc_template())

        self.committee_container.toc_template = self.as_relation_value(
            self.sablon_template)

        self.assertEqual(
            self.sablon_template, self.committee_container.get_toc_template())

    def test_portlets_inheritance_is_blocked(self):
        self.login(self.manager)
        self.assert_portlet_inheritance_blocked(
            'plone.leftcolumn', self.committee_container)

    @browsing
    def test_can_configure_ad_hoc_template(self, browser):
        self.login(self.administrator, browser)
        self.committee_container.ad_hoc_template = None

        self.assertIsNone(self.committee_container.ad_hoc_template)
        self.assertIsNone(self.committee_container.get_ad_hoc_template())

        browser.open(self.committee_container, view='edit')
        browser.fill({'Ad hoc agenda item template': self.proposal_template}).save()
        statusmessages.assert_no_error_messages()

        statusmessages.assert_message('Changes saved')

        self.assertIsNotNone(self.committee_container.ad_hoc_template)
        self.assertEqual(self.proposal_template,
                         self.committee_container.get_ad_hoc_template())

    @browsing
    def test_can_configure_paragraph_template(self, browser):
        self.login(self.administrator, browser)
        self.committee_container.paragraph_template = None

        self.assertIsNone(self.committee_container.paragraph_template)
        self.assertIsNone(self.committee_container.get_paragraph_template())

        browser.open(self.committee_container, view='edit')
        browser.fill({'Paragraph template': self.sablon_template}).save()
        statusmessages.assert_no_error_messages()

        statusmessages.assert_message('Changes saved')

        self.assertIsNotNone(self.committee_container.paragraph_template)
        self.assertEqual(self.sablon_template,
                         self.committee_container.get_paragraph_template())

    @browsing
    def test_can_add_with_templates(self, browser):
        self.login(self.manager, browser)
        browser.open()
        factoriesmenu.add('Committee Container')
        browser.fill({'Title': u'Sitzungen',
                      'Protocol header template': self.sablon_template,
                      'Protocol suffix template': self.sablon_template,
                      'Agenda item header template for the protocol': self.sablon_template,
                      'Agenda item suffix template for the protocol': self.sablon_template,
                      'Excerpt header template': self.sablon_template,
                      'Excerpt suffix template': self.sablon_template,
                      'Paragraph template': self.sablon_template,
                      'Ad hoc agenda item template': self.proposal_template}).save()
        statusmessages.assert_no_error_messages()

        self.assertEqual(self.proposal_template,
                         browser.context.get_ad_hoc_template())
        self.assertEqual(self.sablon_template,
                         browser.context.get_paragraph_template())
        self.assertEqual(self.sablon_template,
                         browser.context.get_excerpt_header_template())
        self.assertEqual(self.sablon_template,
                         browser.context.get_excerpt_suffix_template())

    @browsing
    def test_visible_fields_order_in_form(self, browser):
        fields = [u'Title',
                  u'Protocol header template',
                  u'Protocol suffix template',
                  u'Agenda item header template for the protocol',
                  u'Agenda item suffix template for the protocol',
                  u'Excerpt header template',
                  u'Excerpt suffix template',
                  u'Agendaitem list template',
                  u'Table of contents template',
                  u'Ad hoc agenda item template',
                  u'Paragraph template']
        self.login(self.manager, browser)

        browser.open()
        factoriesmenu.add('Committee Container')
        self.assertEquals(fields, browser.css('form#form > div.field > label').text)

        browser.open(self.committee_container, view='edit')
        self.assertEquals(fields, browser.css('form#form > div.field > label').text)
