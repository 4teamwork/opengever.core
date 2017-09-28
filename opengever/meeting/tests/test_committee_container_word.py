from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase
from ftw.testbrowser.pages import factoriesmenu


class TestCommitteeContainer(IntegrationTestCase):

    features = ('meeting', 'word-meeting')

    @browsing
    def test_can_configure_ad_hoc_template(self, browser):
        self.login(self.administrator, browser)
        self.committee_container.ad_hoc_template = None

        self.assertIsNone(self.committee_container.ad_hoc_template)
        self.assertIsNone(self.committee_container.get_ad_hoc_template())

        browser.open(self.committee_container, view='edit')
        browser.fill({'Ad hoc agenda item template': self.proposal_template}).save()

        statusmessages.assert_message('Changes saved')

        self.assertIsNotNone(self.committee_container.ad_hoc_template)
        self.assertEqual(self.proposal_template,
                         self.committee_container.get_ad_hoc_template())

    @browsing
    def test_can_add_with_ad_hoc_template(self, browser):
        self.login(self.manager, browser)
        browser.open()
        factoriesmenu.add('Committee Container')
        browser.fill({'Title': u'Sitzungen',
                      'Protocol header template': self.sablon_template,
                      'Protocol suffix template': self.sablon_template,
                      'Ad hoc agenda item template': self.proposal_template}).save()
        statusmessages.assert_no_error_messages()

        self.assertEqual(self.proposal_template,
                         browser.context.get_ad_hoc_template())

    @browsing
    def test_can_configure_paragraph_template(self, browser):
        self.login(self.administrator, browser)
        self.committee_container.paragraph_template = None

        self.assertIsNone(self.committee_container.paragraph_template)
        self.assertIsNone(self.committee_container.get_paragraph_template())

        browser.open(self.committee_container, view='edit')
        browser.fill({'Paragraph template': self.sablon_template}).save()

        statusmessages.assert_message('Changes saved')

        self.assertIsNotNone(self.committee_container.paragraph_template)
        self.assertEqual(self.sablon_template,
                         self.committee_container.get_paragraph_template())

    @browsing
    def test_can_add_with_paragraph_template(self, browser):
        self.login(self.manager, browser)
        browser.open()
        factoriesmenu.add('Committee Container')
        browser.fill({'Title': u'Sitzungen',
                      'Protocol header template': self.sablon_template,
                      'Protocol suffix template': self.sablon_template,
                      'Paragraph template': self.sablon_template}).save()
        statusmessages.assert_no_error_messages()

        self.assertEqual(self.sablon_template,
                         browser.context.get_paragraph_template())

    @browsing
    def test_hide_paragraph_template_for_nonword_in_add_form(self, browser):
        """The "Paragraph template" field only makes sense when
        the word-meeting feature is enabled.
        Make sure that it does not appear in the forms when disabling
        the word-meeting feature.
        """
        self.login(self.manager, browser)
        browser.open()
        factoriesmenu.add('Committee Container')
        field_label = 'Paragraph template'
        self.assertTrue(browser.find(field_label))

        self.deactivate_feature('word-meeting')
        browser.reload()
        self.assertFalse(browser.find(field_label))

    @browsing
    def test_hide_paragraph_template_for_nonword_in_edit_form(self, browser):
        """The "Paragraph template" field only makes sense when
        the word-meeting feature is enabled.
        Make sure that it does not appear in the forms when disabling
        the word-meeting feature.
        """
        self.login(self.manager, browser)
        browser.open(self.committee_container, view='edit')
        field_label = 'Paragraph template'
        self.assertTrue(browser.find(field_label))

        self.deactivate_feature('word-meeting')
        browser.reload()
        self.assertFalse(browser.find(field_label))
